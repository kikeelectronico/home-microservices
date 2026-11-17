import json
import logging

import state_handlers
from shutdown import stop_requested, wait_for_stop


STATE_HANDLERS = {
  ("currentModeSettings", "currentFanSpeedSetting"): state_handlers.air_purifier,
  ("on",): state_handlers.on
}


class IkeaOutboundService:

  def __init__(self, ikea):
    self.ikea = ikea

  def run(self):
    while not stop_requested():
      wait_for_stop(1)

  def _handle_message(self, topic, payload):
    # Validate payload
    try:
      payload = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
      logging.warning("Invalid JSON payload on %s: %r", topic, payload)
      return

    if not isinstance(payload, dict):
      logging.warning("Invalid payload type on %s: %r", topic, payload)
      return

    ikea_id = topic.split("/")[1]
    self._handle_state(ikea_id, payload)

  def _handle_state(self, ikea_id, state):
    for required_paths, handler in STATE_HANDLERS.items():
      if all(path in state for path in required_paths):
        handler(self.ikea, ikea_id, state)
        return
