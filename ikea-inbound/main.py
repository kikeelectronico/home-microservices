import paho.mqtt.client as mqtt
import os
import time

from ikea import Ikea
from homeware import Homeware
from logger import Logger

import urllib3
urllib3.disable_warnings()

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
IKEA_HOST = os.environ.get("IKEA_HOST", "no_set")
IKEA_TOKEN = os.environ.get("IKEA_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "ikea-inbound-" + ENV
OUTLET_CURRENT_THRESHOLD = 0.1


# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, logger)
ikea = Ikea(IKEA_HOST, IKEA_TOKEN, logger)

# Main entry point
if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    exit()

  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if IKEA_HOST == "no_set": report("IKEA_HOST env vars no set")
  if IKEA_TOKEN == "no_set": report("IKEA_TOKEN env vars no set")
  
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting " + SERVICE , severity="INFO")
  
  # Main loop
  while True:
    devices = ikea.getDevices()
    for device in devices:
      if device["type"] == "outlet":
        if "isReachable" in device:
          homeware.execute(device["id"], "online", device["isReachable"])
        if "isOn" in device["attributes"]:
          homeware.execute(device["id"], "on", device["attributes"]["isOn"])
        if "currentAmps" in device["attributes"]:
          homeware.execute(device["id"], "isRunning", device["attributes"]["currentAmps"] > OUTLET_CURRENT_THRESHOLD)

    time.sleep(5)
