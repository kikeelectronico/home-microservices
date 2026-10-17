import json
import logging

import param_handlers
from shutdown import stop_requested, wait_for_stop


PARAM_HANDLERS = {
  "on": param_handlers.on,
  "brightness": param_handlers.brightness,
  "color": param_handlers.color,
  "currentToggleSettings": param_handlers.emergency
}


class HueOutboundService:

  def __init__(self, hue):
    self.hue = hue
    self.service_id_device_id = {}
    self.topics = []

  def initialize(self):
    self._load_service_id_device_id()

  def _load_service_id_device_id(self):
    # Map v1 device IDs to light service IDs
    hue_devices = self.hue.getServices(type="device")
    for hue_device in hue_devices:
      # Discard devices without v1 id
      if not hue_device.get("id_v1", False):
        continue

      # Get v1 device id
      hue_v1_device_id = hue_device["id_v1"].split("/")[2]

      # Map device IDs to service IDs
      for service in hue_device["services"]:
        if service.get("rtype", "none") == "light":
          self.service_id_device_id[hue_v1_device_id] = service["rid"]
          self.topics.append("device/hue_" + hue_v1_device_id)

  def run(self):
    while not stop_requested():
      wait_for_stop(1)

  def _handle_message(self, topic, payload):
    # Validate payload
    try:
      payload = json.loads(payload)
    except json.JSONDecodeError:
      logging.warning("Invalid JSON payload on %s: %r", topic, payload)
      return
    if not isinstance(payload, dict):
      logging.warning("Invalid payload type on %s: %r", topic, payload)
      return

    for param, value in payload.items():
      self._handle_param(topic, param, value)

  def _handle_param(self, topic, param, value):
    # Get service ID
    hue_v1_device_id_key = topic.split("hue_")[1]
    hue_service_id = self.service_id_device_id.get(hue_v1_device_id_key)
    if not hue_service_id:
      logging.warning("No hue mapping for key %s on topic %s", hue_v1_device_id_key, topic)
      return

    # Get param handler
    handler = PARAM_HANDLERS.get(param)
    if handler is not None:
      handler(self.hue, hue_service_id, value)
