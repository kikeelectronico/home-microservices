import asyncio
import json
import logging
from asyncio import sleep
from queue import Empty, Queue

from shutdown import stop_requested


class DataPanelService:

  def __init__(self, device_ids):
    self.device_ids = device_ids
    self.mqtt_client = None
    self.sse_queues = set()
    self.mqtt_events = Queue()

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  async def dispatch_mqtt_events(self):
    while not stop_requested():
      try:
        event = self.mqtt_events.get_nowait()
      except Empty:
        await sleep(0.1)
        continue
      for queue in list(self.sse_queues):
        queue.put_nowait(event)

  # Do tasks when a message is received
  def _handle_message(self, topic, payload):
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
      self.mqtt_events.put(event)
    elif topic == "meteo/warnings":
      event = {
        "type": "meteo-warnings",
        "data": data
      }
      self.mqtt_events.put(event)
    elif topic == "meteo/weather":
      event = {
        "type": "meteo-weather",
        "data": data
      }
      self.mqtt_events.put(event)
    elif topic == "internet/status":
      event = {
        "type": "internet-status",
        "data": data
      }
      self.mqtt_events.put(event)
    elif topic == "electricity/grid":
      event = {
        "type": "electricity-grid",
        "data": data
      }
      self.mqtt_events.put(event)
    elif topic == "fire/nearest":
      event = {
        "type": "fire-nearest",
        "data": data
      }
      self.mqtt_events.put(event)
    elif topic.startswith("device"):
      device_id = topic.split("/")[1]
      home = {}
      home[device_id] = data
      event = {
        "type": "home",
        "data": home
      }
      self.mqtt_events.put(event)

  def add_sse_queue(self):
    queue = asyncio.Queue()
    self.sse_queues.add(queue)
    return queue

  def remove_sse_queue(self, queue):
    self.sse_queues.discard(queue)

  async def stream_events(self, queue):
    while not stop_requested():
      try:
        event = queue.get_nowait()
        yield f"data: {json.dumps(event)}\n\n"
        await sleep(0.1)
        continue
      except asyncio.QueueEmpty:
        pass

      await sleep(0.1)

  def request_initial_data(self):
    self.mqtt_client.publish("water/volume/request", "")
    self.mqtt_client.publish("meteo/warnings/request", "")
    self.mqtt_client.publish("meteo/weather/request", "")
    self.mqtt_client.publish("internet/status/request", "")
    self.mqtt_client.publish("electricity/grid/request", "")
    self.mqtt_client.publish("fire/nearest/request", "")
    for device_id in self.device_ids:
      payload = {
        "id": device_id,
        "param":"",
        "value": "",
        "intent":"request"
      }
      self.mqtt_client.publish("device/control", json.dumps(payload))
