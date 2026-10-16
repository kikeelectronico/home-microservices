from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from queue import Queue, Empty
import json
import asyncio
from asyncio import sleep
import logging
from mqtt import set_mqtt_client
from constants import DEVICE_IDS
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
  subscriptions = [
    "water/volume",
    "meteo/warnings",
    "meteo/weather",
    "electricity/grid",
    "internet/status",
    "fire/nearest",
    *[f"device/{device_id}" for device_id in DEVICE_IDS],
    "device/scene_ducha"
  ]
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=subscriptions,
    message_handler=handle_message
  )
  mqtt_events_task = asyncio.create_task(dispatch_mqtt_events())
  try:
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
def handle_message(topic, payload):
  try:
    data = json.loads(payload)
  except json.JSONDecodeError:
    logging.warning("Invalid JSON payload on %s: %r", topic, payload)
    return
  if topic == "water/volume":
    event = {
      "type": "water-volume",
      "data": data
    }
    mqtt_events.put(event)
  elif topic == "meteo/warnings":
    event = {
      "type": "meteo-warnings",
      "data": data
    }
    mqtt_events.put(event)
  elif topic == "meteo/weather":
    event = {
      "type": "meteo-weather",
      "data": data
    }
    mqtt_events.put(event)
  elif topic == "internet/status":
      event = {
        "type": "internet-status",
        "data": data
      }
      mqtt_events.put(event)
  elif topic == "electricity/grid":
      event = {
        "type": "electricity-grid",
        "data": data
      }
      mqtt_events.put(event)
  elif topic == "fire/nearest":
      event = {
        "type": "fire-nearest",
        "data": data
      }
      mqtt_events.put(event)
  elif topic.startswith("device"):
    device_id = topic.split("/")[1]
    home = {}
    home[device_id] = data
    event = {
      "type": "home",
      "data": home
    }
    mqtt_events.put(event)

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
