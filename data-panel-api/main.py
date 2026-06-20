import paho.mqtt.client as mqtt
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from queue import Queue, Empty
import os
import json
import asyncio
from asyncio import sleep
import time
import logging

# from spotify import Spotify
from water import Water
from weather import Weather
from homeware import Homeware
from internet import Internet

# Load env vars
if os.environ.get("ENV", "dev") == "dev":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
MQTT_PORT = 1883
ENV = os.environ.get("ENV", "dev")

# Define constants
SERVICE = "data-panel-api-" + ENV

# Instantiate objects
sse_queues = set()
mqtt_events = Queue()
mqtt_events_task = None

@asynccontextmanager
async def lifespan(app):
  global mqtt_events_task
  mqtt_events_task = asyncio.create_task(dispatch_mqtt_events())
  try:
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
    mqtt_client.loop_start()
    logging.info("Starting " + SERVICE)
    yield
  finally:
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    mqtt_events_task.cancel()
    try:
      await mqtt_events_task
    except asyncio.CancelledError:
      pass
    mqtt_events_task = None

app = FastAPI(lifespan=lifespan)
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
) 

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("meteo/warnings", qos=1)
  logging.info("Subscribed to MQTT topic meteo/warnings")

async def dispatch_mqtt_events():
  while True:
    try:
      event = mqtt_events.get_nowait()
    except Empty:
      await sleep(0.1)
      continue
    for queue in list(sse_queues):
      queue.put_nowait(event)

# Do tasks when a message is received
def on_message(client, userdata, msg):
  if msg.topic != "meteo/warnings":
    logging.warning("Received message on unexpected topic %s", msg.topic)
    return

  try:
    warning = json.loads(msg.payload)
  except json.JSONDecodeError:
    logging.warning("Invalid JSON payload on %s: %r", msg.topic, msg.payload)
    return

  event = {
    "type": "weather-warning",
    "data": warning,
    "flags": {}
  }
  logging.info("Received AEMET warning on %s", msg.topic)
  mqtt_events.put(event)

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while True:
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        time.sleep(5)

# Check env vars
def report(message):
  print(message)
  exit()
if MQTT_USER == "no_set":
  report("MQTT_USER env vars no set")
if MQTT_PASS == "no_set":
  report("MQTT_PASS env vars no set")
if MQTT_HOST == "no_set":
  report("MQTT_HOST env vars no set")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# spotify = Spotify()
water = Water()
weatherapi = Weather()
homeware = Homeware()
internet = Internet()

devices_ids = [
  "current001",
  "thermostat_livingroom",
  "hue_8",
  "ac_001",
  "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
  "temperature_001",
  "df31ac85-be3f-48db-ab5e-483001f3ad27_1",
  "thermostat_bathroom",
  "hue_12",
  "scene_ducha",
  "thermostat_dormitorio",
  "e6c2e2bd-5057-49bc-821f-a4b10e415ac6",
  "temperature_001",
  "switch_at_home"
]

@app.get("/")
async def root():
  return {"message": "Hello, World!"}

async def streamEvents(queue):
  last = {}
  while True:
    try:
      event = queue.get_nowait()
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
      continue
    except asyncio.QueueEmpty:
      pass

    # Internet
    connected = internet.checkConnectivity()
    if not last.get("connected", False) == connected:
      event = {
        "type": "internet",
        "data": {
          "connected": connected
        }
      }
      last["connected"] = connected
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    # Spotify
    # playing = spotify.getPlaying(max_tries=2)
    # if not last.get("playing", {}) == playing:
    #   event = {
    #     "type": "spotify",
    #     "data": {
    #       "playing": playing
    #     }
    #   }
    #   last["playing"] = playing
    #   yield f"data: {json.dumps(event)}\n\n"
    #   await sleep(0.1)
    # Home
    (status_flag, home_status) = homeware.getStatus(devices_ids)
    if not last.get("home_status", {}) == home_status:
      event = {
        "type": "home",
        "data": {
          "status": home_status
        },
        "flags": {
          "status": status_flag
        }
      }
      last["home_status"] = home_status
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
     # Water
    water_data = water.getWater()
    if not last.get("water_data", {}) == water_data:
      event = {
        "type": "water",
        "data": {
          "water": water_data,
        },
        "flags": {}
      }
      last["water_data"] = water_data
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    # Weather
    (fail_to_update, current_flag, current, forecast_flag, forecast, alerts_flag, alerts) = weatherapi.getWeather()
    if not last.get("forecast", {}) == forecast:
      event = {
        "type": "weather",
        "data": {
          "current": current,
          "forecast": forecast,
          "alerts": alerts
        },
        "flags": {
          "current": current_flag,
          "forecast": forecast_flag,
          "alerts": alerts_flag
        }
      }
      last["forecast"] = forecast
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    if time.time() - last.get("ping", 0) > 5:
      event = {
        "type": "ping",
        "data": {},
        "flags": {}
      }
      last["ping"] = time.time()
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)

@app.get("/stream")
async def stream():
  queue = asyncio.Queue()
  sse_queues.add(queue)

  async def stream_with_cleanup():
    try:
      async for event in streamEvents(queue):
        yield event
    finally:
      sse_queues.discard(queue)

  return StreamingResponse(stream_with_cleanup(), media_type="text/event-stream")

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
