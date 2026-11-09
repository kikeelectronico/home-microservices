import json
import logging

import service_handlers
from shutdown import stop_requested, wait_for_stop


SERVICE_HANDLERS = {
  "contact": service_handlers.contact,
  "motion": service_handlers.motion
}


class HueSensorsAlertsService:

  def __init__(self, hue, homeware, mqtt_client):
    self.hue = hue
    self.homeware = homeware
    self.mqtt_client = mqtt_client

  def run(self):
    self._listen_for_events()

  def _listen_for_events(self):
    while not stop_requested():
      client = None
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

      except Exception:
        if stop_requested():
          break
        logging.exception("Hue SSE stream failed. Reconnecting in 5s...")
      finally:
        if client is not None:
          client.close()

      if not stop_requested():
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
    handler = SERVICE_HANDLERS.get(service.get("type"))
    if handler is not None:
      handler(self.homeware, self.mqtt_client, service)
