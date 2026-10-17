import json
import logging

import init
import services
from shutdown import stop_requested, wait_for_stop


SERVICE_HANDLERS = {
  "contact": services.contact,
  "motion": services.motion,
  "zigbee_connectivity": services.connectivity,
  "device_power": services.power,
  "light_level": services.lightlevel,
  "light": services.light
}


class HueInboundService:

  def __init__(self, hue, homeware):
    self.hue = hue
    self.homeware = homeware
    self.device_id_service_id = {}

  def initialize(self):
    self._load_device_id_service_id()
    self._load_initial_values()

  def run(self):
    self._listen_for_events()

  def _load_device_id_service_id(self):
    # Get devices ids relation
    hue_devices = self.hue.getServices(type="device")
    for hue_device in hue_devices:
      for service in hue_device.get("services", []):
        self.device_id_service_id[service["rid"]] = hue_device["id"]

  def _load_initial_values(self):
    # Get initial values
    init.contact(self.hue, self.homeware, self.device_id_service_id)
    init.motion(self.hue, self.homeware, self.device_id_service_id)
    init.connectivity(self.hue, self.homeware, self.device_id_service_id)
    init.power(self.hue, self.homeware, self.device_id_service_id)
    init.lightlevel(self.hue, self.homeware, self.device_id_service_id)

  def _listen_for_events(self):
    while not stop_requested():
      try:
        # Connect to Hue bridge
        client = self.hue.getEventStreamClient()
        if client is None:
          break

        # Handle events
        for message in client.events():
          if stop_requested():
            break
          self._handle_message(message.data)

        if stop_requested():
          break
        logging.warning("Hue SSE stream closed. Reconnecting in 5s...")
        wait_for_stop(5)

      except Exception:
        if stop_requested():
          break
        logging.exception("Hue SSE stream failed. Reconnecting in 5s...")
        wait_for_stop(5)

  def _handle_message(self, message_data):
    try:
      events = json.loads(message_data)
    except ValueError:
      logging.warning("Invalid SSE JSON payload: %r", message_data)
      return

    if not isinstance(events, list):
      logging.warning("Invalid SSE payload type: %r", events)
      return

    for event in events:
      data = event.get("data") if isinstance(event, dict) else None
      if not isinstance(data, list):
        logging.warning("Invalid SSE event data type: %r", event)
        continue

      for service in data:
        self._handle_service(service)

  def _handle_service(self, service):
    if not isinstance(service, dict):
      logging.warning("Invalid Hue service payload: %r", service)
      return

    handler = SERVICE_HANDLERS.get(service.get("type"))
    if handler is not None:
      handler(service, self.homeware, self.device_id_service_id)
