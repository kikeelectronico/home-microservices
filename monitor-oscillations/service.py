import time

from constants import HEARTBEAT_TOPIC, OSCILLATION_THRESHOLD


class MonitorOscillationsService:

  def __init__(self):
    self.mqtt_client = None
    self.last_status = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def _handle_message(self, topic, payload):
    if topic == HEARTBEAT_TOPIC:
      for status_id in self.last_status:
        if self.last_status[status_id]["oscillating"]:
          if time.time() - self.last_status[status_id]["timestamp"] > OSCILLATION_THRESHOLD:
            self.mqtt_client.publish(f"oscillation/{status_id}", "reset")
            self.last_status[status_id]["counter"] = 0
            self.last_status[status_id]["oscillating"] = False
      return

    status_id = topic.split("device/")[1]
    if self.last_status.get(status_id):
      if payload != self.last_status[status_id]["value"]:
        if time.time() - self.last_status[status_id]["timestamp"] < OSCILLATION_THRESHOLD:
          if self.last_status[status_id]["counter"] == 0:
            self.last_status[status_id]["counter"] = 1
          else:
            self.mqtt_client.publish(f"oscillation/{status_id}", "set")
            self.last_status[status_id]["oscillating"] = True
        self.last_status[status_id]["value"] = payload
        self.last_status[status_id]["timestamp"] = time.time()
    else:
      self.last_status[status_id] = {
        "timestamp": time.time(),
        "value": payload,
        "counter": 0,
        "oscillating": False
      }
