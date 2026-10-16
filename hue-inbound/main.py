import json
import logging

from mqtt import set_mqtt_client
from hue import Hue
from homeware import Homeware
import init
import services
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
device_id_service_id = {}
settings = None
mqtt_client = None
homeware = None
hue = None

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
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  hue = Hue(settings.hue_host, settings.hue_token)
  
  mqtt_client.loop_start()

  # Get devices ids relation
  hue_devices = hue.getServices(type="device")
  for hue_device in hue_devices:
    for service in hue_device["services"]:
      device_id_service_id[service["rid"]] = hue_device["id"]

  # Get initial values
  init.contact(hue, homeware, device_id_service_id)
  init.motion(hue, homeware, device_id_service_id)
  init.connectivity(hue, homeware, device_id_service_id)
  init.power(hue, homeware, device_id_service_id)
  init.lightlevel(hue, homeware, device_id_service_id)

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
            if service["type"] == "contact":
              services.contact(service, homeware, device_id_service_id)
            elif service["type"] == "motion":
              services.motion(service, homeware, device_id_service_id)
            elif service["type"] == "zigbee_connectivity":
              services.connectivity(service, homeware, device_id_service_id)
            elif service["type"] == "device_power":
              services.power(service, homeware, device_id_service_id)
            elif service["type"] == "light_level":
              services.lightlevel(service, homeware, device_id_service_id)
            elif service["type"] == "light":
              services.light(service, homeware, device_id_service_id)

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
