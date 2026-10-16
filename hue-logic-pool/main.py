import paho.mqtt.client as mqtt
import json
import logging

from constants import MQTT_PORT
from homeware import Homeware
from hue import Hue
import buttons
import dimmers
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
last_pressed = {}
settings = None
mqtt_client = None
homeware = None
hue = None

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        wait_for_stop(5)

# Main entry point
if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting %s", settings.service_id)

  # Instantiate objects
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  hue = Hue(settings.hue_host, settings.hue_token)
  
  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()

  while not stop_requested():
    try:
      # Connect to Hue bridge
      client = hue.getEventStreamClient()
      if client is None:
        break
      
      # Handle events
      for message in client.events():
        if stop_requested():
          break
        try:
          events = json.loads(message.data)
        except ValueError:
          logging.warning("Invalid SSE JSON payload: %r", message.data)
          continue
        if not isinstance(events, list):
          logging.warning("Invalid SSE payload type: %r", events)
          continue
        for event in events:
          data = event.get("data") if isinstance(event, dict) else None
          if not isinstance(data, list):
            logging.warning("Invalid SSE event data type: %r", event)
            continue
          for service in data:
            if service["id"] == "a4ac42ce-414e-483b-b13c-0f2c5e7dc879":
              buttons.bedroom(service, homeware)
            elif service["id"] == "3ea75bb9-6bf6-4a2e-8f85-f9013e6279bc":
              buttons.kitchen(service, homeware)
            elif service["id"] == "04db1f5f-3467-4a26-9e17-7d9e6586a536":
              buttons.bathroom(service, homeware)
            else:
              dimmers.mirror(service, homeware)

      if stop_requested():
        break
      logging.warning("Hue SSE stream closed. Reconnecting in 5s...")
      wait_for_stop(5)

    except Exception:
      if stop_requested():
        break
      logging.exception("Hue SSE stream failed. Reconnecting in 5s...")
      wait_for_stop(5)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")
