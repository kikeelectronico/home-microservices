import paho.mqtt.client as mqtt
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from queue import Queue, Empty
import json
import asyncio
from asyncio import sleep
import logging
from constants import DEVICE_IDS, MQTT_PORT
from settings import Settings
from shutdown import request_stop, stop_requested, wait_for_stop

# from spotify import Spotify

# Instantiate objects
sse_queues = set()
mqtt_events = Queue()
mqtt_events_task = None
settings = None
mqtt_client = None

@asynccontextmanager
async def lifespan(app):
  global mqtt_events_task, settings, mqtt_client
  settings = Settings()
  settings.load_settings()
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )
  mqtt_events_task = asyncio.create_task(dispatch_mqtt_events())
  try:
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
    mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
    mqtt_client.loop_start()
    logging.info("Starting " + settings.service_id)
    yield
  finally:
    request_stop()
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    mqtt_events_task.cancel()
    try:
      await mqtt_events_task
    except asyncio.CancelledError:
      pass
    mqtt_events_task = None

app = FastAPI(lifespan=lifespan)

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("water/volume", qos=1)
  client.subscribe("meteo/warnings", qos=1)
  client.subscribe("meteo/weather", qos=1)
  client.subscribe("electricity/grid", qos=1)
  client.subscribe("internet/status", qos=1)
  client.subscribe("fire/nearest", qos=1)
  for topic in DEVICE_IDS:
    client.subscribe(f"device/{topic}", qos=1)
  client.subscribe("device/scene_ducha", qos=1)

async def dispatch_mqtt_events():
  while not stop_requested():
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
  if msg.topic == "water/volume":
    event = {
      "type": "water-volume",
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
  elif msg.topic == "internet/status":
      event = {
        "type": "internet-status",
        "data": data
      }
      mqtt_events.put(event)
  elif msg.topic == "electricity/grid":
      event = {
        "type": "electricity-grid",
        "data": data
      }
      mqtt_events.put(event)
  elif msg.topic == "fire/nearest":
      event = {
        "type": "fire-nearest",
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
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
      wait_for_stop(5)

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
  while not stop_requested():
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
  mqtt_client.publish("water/volume/request", "")
  mqtt_client.publish("meteo/warnings/request", "")
  mqtt_client.publish("meteo/weather/request", "")
  mqtt_client.publish("internet/status/request", "")
  mqtt_client.publish("electricity/grid/request", "")
  mqtt_client.publish("fire/nearest/request", "")
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
