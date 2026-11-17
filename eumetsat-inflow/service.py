import json
import time

from constants import NEAREST_FIRE_INTERVAL, NEAREST_FIRE_REQUEST_TOPIC, NEAREST_FIRE_TOPIC
from eumetsat import getNearestFire


class EumetsatInflowService:

  def __init__(self, settings):
    self.settings = settings
    self.mqtt_client = None
    self.last_nearest_fire_timestamp = 0
    self.last_nearest_fire_payload = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def update_if_due(self):
    now = time.time()
    if now - self.last_nearest_fire_timestamp > NEAREST_FIRE_INTERVAL:
      self._publish_nearest_fire()
      self.last_nearest_fire_timestamp = time.time()

  def _publish_nearest_fire(self, force=False):
    nearest_fire = getNearestFire(
      consumer_key=self.settings.eumetsat_consumer_key,
      consumer_secret=self.settings.eumetsat_consumer_secret,
      ref_lat=float(self.settings.reference_lat),
      ref_lon=float(self.settings.reference_lon),
      bbox=self.settings.bounding_box
    )
    if not nearest_fire:
      return

    if force or nearest_fire != self.last_nearest_fire_payload:
      self.mqtt_client.publish(NEAREST_FIRE_TOPIC, json.dumps(nearest_fire))
      self.last_nearest_fire_payload = nearest_fire

  def _handle_message(self, topic, payload):
    if topic == NEAREST_FIRE_REQUEST_TOPIC:
      self._publish_nearest_fire(force=True)
