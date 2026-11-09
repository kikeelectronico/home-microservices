import json

from Internet import getInternetStatus
from constants import STATUS_REQUEST_TOPIC, STATUS_TOPIC


class InternetInflowService:

  def __init__(self):
    self.mqtt_client = None
    self.last_status = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def publish_status(self, force=False):
    internet_status = getInternetStatus()

    if force or internet_status != self.last_status:
      self.mqtt_client.publish(STATUS_TOPIC, json.dumps(internet_status))
      self.last_status = internet_status

  def update_if_due(self):
    self.publish_status()

  def _handle_message(self, topic, payload):
    if topic == STATUS_REQUEST_TOPIC:
      self.publish_status(force=True)
