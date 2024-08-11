import paho.mqtt.client as mqtt
import os
import time
import pychromecast

from homeware import Homeware
from logger import Logger
import logic


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
SLEEP_TIME = 0.1
SERVICE = "chromecast-logic-pool-" + ENV

# Declare variables
last_heartbeat_timestamp = 0

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, logger)

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
  
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting " + SERVICE , severity="INFO")

  # Connect to the tv
  chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Tele"])
  device = chromecasts[0]
  device.wait()
  while True:
    if not device.app_display_name == None:
      device_controller = device.media_controller
      device_controller.block_until_active(5)
      if device_controller.status.player_state in ["IDLE", "UNKNOWN"]:
        logic.notPlayingLights(homeware)
      if device_controller.status.player_state == "PLAYING":
        logic.playingLights(homeware)
    time.sleep(5)