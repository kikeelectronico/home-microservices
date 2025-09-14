import paho.mqtt.client as mqtt
import os
import time
import functions
import logging

# Load env vars
if os.environ.get("MQTT_PASS", "pass") == "pass":
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
SLEEP_TIME = 10
BLOCK_TIME = 300
SERVICE = "monitor-http-request-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE) 

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

  # Main loop
  while True:
    # Verify Homeware connectivity
    if not functions.homewareTest(HOMEWARE_API_URL, HOMEWARE_API_KEY):
      logging.warning("Homeware no responde")
      mqtt_client.publish("voice-alert/text", "Homeware no responde")
      mqtt_client.publish("message-alerts", "Homeware no responde")
      time.sleep(BLOCK_TIME)
    # Verify Hue Bridge connectivity
    if not functions.hueTest(HUE_HOST, HUE_TOKEN):
      logging.warning("Hue bridge no responde")
      mqtt_client.publish("voice-alert/text", "Hue bridge no responde")
      mqtt_client.publish("message-alerts", "Hue bridge no responde")
      time.sleep(BLOCK_TIME)
    # Send heartbeart
    mqtt_client.publish("heartbeats", SERVICE)
    # Wait until next iteration
    time.sleep(SLEEP_TIME)

    