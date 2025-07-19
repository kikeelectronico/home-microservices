from cmath import e
import paho.mqtt.client as mqtt
import os

import functions
from Homeware import Homeware
from logger import Logger
from Alert import Alert
import lights
import air
import scenes

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
  "heartbeats/request",
  "device/thermostat_bathroom",
  "device/switch_hood/on",
  "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
  "device/hue_11/color",
  "device/hue_11/brightness",
  "device/hue_4/brightness",
  "device/hue_5/brightness",
  "device/hue_4/color",
  "device/hue_5/color",
  "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness",
  "device/pressure001/occupancy",
  "device/scene_dim/enable"
]
SERVICE = "device-controller-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, logger)
alert = Alert(mqtt_client, logger)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
  for topic in TOPICS:
    client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
  try:
    if msg.topic == "heartbeats/request":
      # Send heartbeat
      mqtt_client.publish("heartbeats", SERVICE)
    else:
      # Exec the logic
      payload = functions.loadPayload(msg.payload)
      if payload is not None:
        air.hood(homeware, msg.topic, payload)
        lights.resetEdisonBulb(homeware, msg.topic, payload)
        lights.mirrorPyramids(homeware, msg.topic, payload)
        lights.sofaLight(homeware, msg.topic, payload)
        # scenes.livingroomLight(homeware, msg.topic, payload)
  except Exception as e:
    logger.log("Excepción en Logic pool mqtt", severity="WARNING")
    logger.log(str(e), severity="WARNING") 

if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    #logger.log(message, severity="ERROR")
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
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting " + SERVICE , severity="INFO")
  # Main loop
  mqtt_client.loop_forever()