from cmath import e
import paho.mqtt.client as mqtt
import os
import openai

import functions
from Homeware import Homeware
from logger import Logger
from Alert import Alert
import alerts
import power
import general
import scenes
import switches
import thermostats

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = [
  "heartbeats/request",
  "device/thermostat_bathroom/capacityRemaining",
  "device/thermostat_dormitorio/capacityRemaining",
  "device/thermostat_livingroom/capacityRemaining",
  "device/thermostat_livingroom",
  "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
  "device/switch_at_home/on",
  "device/switch_prepare_home/on",
  "device/scene_ducha/enable",
  "device/current001/brightness",
  "device/thermostat_livingroom",
  "device/thermostat_bathroom",
  "device/thermostat_dormitorio",
  "device/switch_at_home/on"
  "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
  "device/hue_sensor_12/on",
  "device/hue_sensor_14/on",
  "device/hue_sensor_2/on",
  "device/thermostat_livingroom",
  "device/scene_dim/enable",
  "device/scene_ducha/enable",
  "device/thermostat_bathroom",
  "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/occupancy",
  "device/control"
]
SERVICE = "logic-pool-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, logger)
alert = Alert(mqtt_client, openai, logger)

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
        alerts.battery(homeware, alert, msg.topic, payload)
        alerts.abnormalLivingroomTemperature(homeware, alert, msg.topic, payload)
        general.atHome(homeware, msg.topic, payload)
        general.prepareHome(homeware, msg.topic, payload)
        power.powerManagment(homeware, msg.topic, payload)
        scenes.dim(homeware, msg.topic, payload)
        scenes.shower(homeware, alert, msg.topic, payload)
        scenes.disableShowerScene(homeware, alert, msg.topic, payload)
        scenes.powerAlert(homeware, alert, msg.topic, payload)
        switches.bedroom(homeware, msg.topic, payload)
        switches.bathroom(homeware, msg.topic, payload)
        switches.mirror(homeware, msg.topic, payload)
        thermostats.livingroom(homeware, msg.topic, payload)
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
  if OPENAI_API_KEY == "no_set":
    report("OPENAI_API_KEY env vars no set")
  # Set the API key for OpenAI
  openai.api_key = OPENAI_API_KEY
  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting " + SERVICE , severity="INFO")
  # Main loop
  mqtt_client.loop_forever()