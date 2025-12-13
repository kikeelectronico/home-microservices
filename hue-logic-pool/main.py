import paho.mqtt.client as mqtt
import os
import json
from sseclient import SSEClient
import requests
import logging

from homeware import Homeware
import buttons
import dimmers
import sensors

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
HUE_HOST = os.environ.get("HUE_HOST", "no_set")
HUE_TOKEN = os.environ.get("HUE_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SLEEP_TIME = 0.1
SERVICE = "hue-logic-pool-" + ENV

# Declare variables
last_heartbeat_timestamp = 0
last_pressed = {}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

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
  if HUE_HOST == "no_set": report("HUE_HOST env vars no set")
  if HUE_TOKEN == "no_set": report("HUE_TOKEN env vars no set")
  
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logging.info("Starting " + SERVICE)

  # Connect to Hue bridge
  url = "https://" + HUE_HOST + "/eventstream/clip/v2"
  headers = {
    'hue-application-key': HUE_TOKEN,
    'Accept': 'text/event-stream'
  }
  stream_response = requests.get(url, headers=headers, stream=True, verify=False)
  client = SSEClient(stream_response)
  
  # Handle events
  for message in client.events():
    for event in json.loads(message.data):
      for service in event["data"]:
        buttons.bedroom(service, homeware)
        buttons.kitchen(service, homeware)
        buttons.bathroom(service, homeware)
        dimmers.mirror(service, homeware)
        sensors.bedroom(service, homeware, mqtt_client)
        sensors.bathroom(service, homeware, mqtt_client)
        sensors.hall(service, homeware)
        sensors.livingroom_motion(service, homeware, mqtt_client)
        sensors.livingroom_light(service, homeware)
