import logging

import functions
from constants import (
  BLOCK_TIME,
  HEARTBEAT_TOPIC,
  SLEEP_TIME,
  TEXT_ALERT_TOPIC,
  VOICE_ALERT_TOPIC
)


class MonitorHttpRequestService:

  def __init__(self, settings, mqtt_client):
    self.settings = settings
    self.mqtt_client = mqtt_client

  def check_connections(self):
    if not functions.homeware_test(self.settings.homeware_api_url, self.settings.homeware_api_key):
      self._send_alert("Homeware no responde")
      return BLOCK_TIME

    if not functions.hue_test(self.settings.hue_host, self.settings.hue_token):
      self._send_alert("Hue bridge no responde")
      return BLOCK_TIME

    if not functions.ikea_test(self.settings.ikea_host, self.settings.ikea_token):
      self._send_alert("Ikea bridge no responde")
      return BLOCK_TIME

    self.mqtt_client.publish(HEARTBEAT_TOPIC, self.settings.service_id)
    return SLEEP_TIME

  def _send_alert(self, message):
    logging.warning(message)
    self.mqtt_client.publish(VOICE_ALERT_TOPIC, message)
    self.mqtt_client.publish(TEXT_ALERT_TOPIC, message)
