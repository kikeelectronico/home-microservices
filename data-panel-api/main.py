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
DEVICE_IDS = [
  "current001",
  "thermostat_livingroom",
  "fecf95fe-7cf3-4cc1-87bc-98e5669320f8_1",
  "ac_001",
  "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
  "temperature_001",
  "df31ac85-be3f-48db-ab5e-483001f3ad27_1",
  "thermostat_bathroom",
  "9339195d-75c3-4fc1-aeac-03f8af899e40_1",
  "thermostat_dormitorio",
  "e6c2e2bd-5057-49bc-821f-a4b10e415ac6",
  "temperature_001",
  "switch_at_home"
]

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
  client.subscribe("water", qos=1)
  logging.info("Subscribed to MQTT topic water")
  client.subscribe("meteo/warnings", qos=1)
  logging.info("Subscribed to MQTT topic meteo/warnings")
  client.subscribe("meteo/weather", qos=1)
  logging.info("Subscribed to MQTT topic meteo/weather")
  for topic in DEVICE_IDS:
    client.subscribe(f"device/{topic}", qos=1)
  client.subscribe("device/scene_ducha", qos=1)

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
  try:
    data = json.loads(msg.payload)
  except json.JSONDecodeError:
    logging.warning("Invalid JSON payload on %s: %r", msg.topic, msg.payload)
    return
  if msg.topic == "water":
    event = {
      "type": "water",
      "data": data
    }
    mqtt_events.put(event)
  elif msg.topic == "meteo/warnings":
    event = {
      "type": "meteo-warnings",
      "data": data
    }
    mqtt_events.put(event)
  elif msg.topic == "meteo/weather":
    event = {
      "type": "meteo-weather",
      "data": data
    }
    mqtt_events.put(event)
  elif msg.topic == "internet":
      event = {
        "type": "internet",
        "data": data
      }
      mqtt_events.put(event)
  elif msg.topic.startswith("device"):
    device_id = msg.topic.split("/")[1]
    home = {}
    home[device_id] = data
    event = {
      "type": "home",
      "data": home
    }
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

    await sleep(0.1)

@app.get("/stream")
async def stream():
  queue = asyncio.Queue()
  sse_queues.add(queue)
  mqtt_client.publish("water/request", "")
  mqtt_client.publish("meteo/warnings/request", "")
  mqtt_client.publish("meteo/weather/request", "")
  mqtt_client.publish("internet/request", "")
  for device_id in DEVICE_IDS:
    payload = {
      "id": device_id,
      "param":"",
      "value": "",
      "intent":"request"
    }
    mqtt_client.publish("device/control", json.dumps(payload))

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
