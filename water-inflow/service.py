import json
import time

from constants import WATER_INTERVAL, WATER_REQUEST_TOPIC, WATER_TOPIC
from water import getWater


class WaterInflowService:

  def __init__(self):
    self.mqtt_client = None
    self.last_volume_timestamp = 0
    self.last_volume_payload = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def update_if_due(self):
    now = time.time()
    if now - self.last_volume_timestamp > WATER_INTERVAL:
      self._publish_volume()
      self.last_volume_timestamp = time.time()

  def _publish_volume(self, force=False):
    water_payload = getWater()
    if not water_payload:
      return

    if force or water_payload != self.last_volume_payload:
      self.mqtt_client.publish(WATER_TOPIC, json.dumps(water_payload))
      self.last_volume_payload = water_payload

  def _handle_message(self, topic, payload):
    if topic == WATER_REQUEST_TOPIC:
      self._publish_volume(force=True)
