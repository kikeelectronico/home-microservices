import json
import logging
import time

from constants import POWER_CONSTANT


class BigQueryOutboundService:

  def __init__(self):
    self.settings = None
    self.bigquery_client = None
    self.last_value = {}

  def initialize(self, settings, bigquery_client):
    self.settings = settings
    self.bigquery_client = bigquery_client

  # Change the type of the payload
  def _typify_payload(self, topic, payload):
    if "heartbeats" in topic:
      return payload
    elif "Temperature" in topic:
      return float(payload)
    elif "temperature" in topic:
      return float(payload)
    elif "currentSensorStateData" in topic:
      return json.loads(payload.replace("'", '"'))
    else:
      return int(payload)

  # Handle a task when a message is received
  def _handle_message(self, topic, payload):
    try:
      payload = self._typify_payload(topic, payload.decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
      logging.warning("Invalid payload on %s: %r (%s)", topic, payload, exc)
      return

    # The request depends on the device
    if payload != self.last_value.setdefault(topic, 0):
      try:
        # Prepare the data
        ts = int(time.time())
        device_id = topic.split("/")[1]
        states = []
        if "current001" in topic:
          states.append(
            {
              "param": "current",
              "value": payload * POWER_CONSTANT
            }
          )
        elif "currentSensorStateData" in topic:
          if not isinstance(payload, list):
            logging.warning("Invalid currentSensorStateData payload type on %s: %r", topic, payload)
            return
          for sensor in payload:
            if not isinstance(sensor, dict):
              logging.warning("Invalid sensor payload on %s: %r", topic, sensor)
              return
            if "name" not in sensor or "rawValue" not in sensor:
              logging.warning("Missing sensor fields on %s: %r", topic, sensor)
              return
            states.append(
              {
                "param": sensor["name"],
                "value": sensor["rawValue"]
              }
            )
        else:
          states.append(
            {
              "param": topic.split("/")[2],
              "value": payload
            }
          )
      except (IndexError, KeyError, TypeError) as exc:
        logging.warning("Invalid message structure on %s: %s", topic, exc)
        return

      try:
        for state in states:
          # Insert the data
          query_job = self.bigquery_client.query(
            """
              INSERT INTO {}
              (time, device_id, param, value, type)
              VALUES ({},"{}","{}","{}", "{}");
            """.format(self.settings.device_ddbb, ts, device_id, state["param"], str(state["value"]), state["value"].__class__.__name__)
          )
          query_job.result()
        # Update last_value
        self.last_value[topic] = payload
      except Exception as exc:
        logging.warning(
          "Fail to insert state into BigQuery on %s: device_id=%s param=%s value=%r error=%s",
          topic,
          device_id,
          state.get("param"),
          state.get("value"),
          exc
        )
