import json
import logging

import device_handlers
import pending_tasks


DEVICE_HANDLERS = {
  "outlet": device_handlers.outlet,
  "motionSensor": device_handlers.motion_sensor,
  "airPurifier": device_handlers.air_purifier,
  "environmentSensor": device_handlers.environment_sensor,
  "waterSensor": device_handlers.water_leak_sensor
}


class IkeaInboundService:

  def __init__(self, ikea, homeware):
    self.ikea = ikea
    self.homeware = homeware
    self.tasks = {}
    self.voltages_map = {}

  def run(self):
    # Run the IKEA WebSocket event stream
    self.ikea.run_event_stream(self._handle_message)

  def _handle_message(self, message):
    try:
      event = json.loads(message)
    except (json.JSONDecodeError, TypeError):
      logging.warning("Invalid IKEA WebSocket JSON payload: %r", message)
      return

    if not isinstance(event, dict):
      logging.warning("Invalid IKEA WebSocket event type: %r", event)
      return

    data = event.get("data")
    if not isinstance(data, dict):
      logging.warning("Invalid IKEA WebSocket event data type: %r", event)
      return

    if "lastModified" in data:
      return

    attributes = data.get("attributes")
    if not isinstance(attributes, dict):
      logging.warning("Invalid IKEA WebSocket attributes type: %r", data)
      return

    self._handle_device(data)
    pending_tasks.process(self.homeware, self.tasks)

  def _handle_device(self, data):
    # Get device handler
    handler = DEVICE_HANDLERS.get(data.get("deviceType"))
    if handler is None:
      return

    if data["deviceType"] == "outlet":
      handler(self.homeware, data, self.tasks, self.voltages_map)
    else:
      handler(self.homeware, data)

