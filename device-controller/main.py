import paho.mqtt.client as mqtt
import os
import logging
import time

import functions
from Homeware import Homeware
from Alert import Alert
import lights

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = [
  "device/thermostat_bathroom",
  "device/switch_hood/on",
  "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
  "device/hue_11/color",
  "device/hue_11/brightness",
  "device/hue_17/color",
  "device/hue_17/brightness",
  "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness",
  "device/pressure001/occupancy",
  "device/temp_switch/on",
  "device/0b97c3c8-cb02-4f6d-9e60-d5755b25b968_1/occupancy",
  "device/scene_dim/enable"
]
SERVICE = "device-controller-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)
alert = Alert(mqtt_client)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
  for topic in TOPICS:
    client.subscribe(topic, qos=1)

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

# Do tasks when a message is received
def on_message(client, userdata, msg):
  try:
    # Exec the logic
    payload = functions.loadPayload(msg.payload)
    if payload is not None:
      lights.workbenchLight(homeware, msg.topic, payload)
      lights.worktableLight(homeware, msg.topic, payload)
  except Exception as e:
    logging.warning("Excepción en Logic pool mqtt")
    logging.warning(str(e)) 

if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    #logging.error(message)
    exit()
  if MQTT_USER == "no_set":
    report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set":
    report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set":
    report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set":
    report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set":
    report("HOMEWARE_API_KEY env vars no set")
  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  logging.info("Starting " + SERVICE)
  # Main loop
  mqtt_client.loop_forever()
