import json
import time

from constants import ESIOS_INTERVAL, GRID_REQUEST_TOPIC, GRID_TOPIC
from esios import getEsiosIndicator


class ElectricityInflowService:

  def __init__(self, settings):
    self.settings = settings
    self.mqtt_client = None
    self.last_grid_timestamp = 0
    self.last_grid_payload = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def update_if_due(self):
    now = time.time()
    if now - self.last_grid_timestamp > ESIOS_INTERVAL:
      self._publish_grid()
      self.last_grid_timestamp = time.time()

  def _publish_grid(self, force=False):
    grid_payload = getEsiosIndicator(self.settings.esios_api_key, 10033)
    if not grid_payload:
      return

    if force or grid_payload != self.last_grid_payload:
      self.mqtt_client.publish(GRID_TOPIC, json.dumps(grid_payload))
      self.last_grid_payload = grid_payload

  def _handle_message(self, topic, payload):
    if topic == GRID_REQUEST_TOPIC:
      self._publish_grid(force=True)
