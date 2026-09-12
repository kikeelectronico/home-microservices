import paho.mqtt.client as mqtt
import os
import logging
import sys

from config import RULES
from homeware import Homeware
from mqtt_handlers import on_disconnect
from rules import evaluateRules
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

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
SLEEP_TIME = 10
SERVICE = "monitor-cause-effect-" + ENV

# Create vars for objects
mqtt_client = None 
homeware = None

# Main entry point
if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )

  # Register shutdown handlers
  register_shutdown_handlers()

  # Check env vars
  def report(message):
    logging.error(message)
    logging.info("Waiting 30 seconds before exiting.")
    wait_for_stop(30)
    logging.info("Exiting program.")
    sys.exit(1)

  if MQTT_USER == "no_set": report("MQTT_USER env vars no set.")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set.")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set.")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set.")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set.")

  # Create mqtt client
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=SERVICE,
    protocol=mqtt.MQTTv5
  ) 
  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  logging.info(f"Starting {SERVICE}.")

  # Create homeware object
  homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

  # Main loop
  while not stop_requested():
    # Evaluate rules
    evaluateRules(homeware, mqtt_client, RULES)

    # Send heartbeat
    mqtt_client.publish("heartbeats", SERVICE)

    # Wait until next iteration
    wait_for_stop(SLEEP_TIME)

  # Clean shutdown
  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

    
