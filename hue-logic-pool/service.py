import json
import logging

import buttons
import dimmers
from shutdown import stop_requested, wait_for_stop


BUTTON_HANDLERS = {
  "a4ac42ce-414e-483b-b13c-0f2c5e7dc879": buttons.bedroom,
  "3ea75bb9-6bf6-4a2e-8f85-f9013e6279bc": buttons.kitchen,
  "04db1f5f-3467-4a26-9e17-7d9e6586a536": buttons.bathroom,
}

DIMMER_HANDLERS = {
  "eef00948-5ed7-4ec4-94dd-60da620887a1": dimmers.mirror_on_off,
  "13362cd4-0324-4dfb-97ec-c567c2cefb70": dimmers.mirror_brightness_up,
  "17bd6fda-f053-403e-ab85-4ab3efa77abe": dimmers.mirror_brightness_down,
  "ee82e035-fd34-45d8-bbf2-282980004c63": dimmers.mirror_color_temperature
}


class HueLogicPoolService:

  def __init__(self, hue, homeware):
    self.hue = hue
    self.homeware = homeware
    self.buttons_preloaded_data = {}
    self.dimmers_preloaded_data = {}

  def run(self):
    self._listen_for_events()

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
    # Validate payload
    try:
      events = json.loads(message_data)
    except json.JSONDecodeError:
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

    # Get service handler
    handler = BUTTON_HANDLERS.get(service.get("id"))
    if handler is not None:
      handler(self.homeware, service, self.buttons_preloaded_data)
      return

    handler = DIMMER_HANDLERS.get(service.get("id"))
    if handler is not None:
      handler(self.homeware, service, self.dimmers_preloaded_data)
