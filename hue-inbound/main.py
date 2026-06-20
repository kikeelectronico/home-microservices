import paho.mqtt.client as mqtt
import os
import json
import logging
import time

from hue import Hue
from homeware import Homeware
import init
import services

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
HUE_HOST = os.environ.get("HUE_HOST", "no_set")
HUE_TOKEN = os.environ.get("HUE_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "hue-inbound-" + ENV

# Declare variables
device_id_service_id = {}

# Instantiate objects
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)
hue = Hue(HUE_HOST, HUE_TOKEN)

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while True:
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        time.sleep(5)

# Main entry point
if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if HUE_HOST == "no_set": report("HUE_HOST env vars no set")
  if HUE_TOKEN == "no_set": report("HUE_TOKEN env vars no set")
  
  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)

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

  while True:
    try:
      # Connect to Hue bridge
      client = hue.getEventStreamClient()
      
      # Handle events
      for message in client.events():
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

      logging.warning("Hue SSE stream closed. Reconnecting in 5s...")
      time.sleep(5)
    
    except Exception:
        logging.exception("Hue SSE stream failed. Reconnecting in 5s...")
        time.sleep(5)
