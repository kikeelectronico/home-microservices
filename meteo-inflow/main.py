import paho.mqtt.client as mqtt
import os
import time
import logging
import json

from weather import getWeather
from weather_warnings import getWarnings

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
WHEATHER_API_KEY = os.environ.get("WHEATHER_API_KEY", "no_set")
WHEATHER_QUERY = os.environ.get("WHEATHER_QUERY", "no_set")
AEMET_RSS = os.environ.get("AEMET_RSS", "no_set")
AEMET_AREA = os.environ.get("AEMET_AREA", "no_set")
ENV = os.environ.get("ENV", "dev")


# Define constants
MQTT_PORT = 1883
SERVICE = "meteo-inflow-" + ENV
REQUEST_TIMEOUT = 10
SLEEP_TIME = 10
WARNINGS_INTERVAL = 1800
WEATHER_INTERVAL = 1800

# Declare variables
last_heartbeat_timestamp = 0
last_warnings_timestamp = 0
last_weather_timestamp = 0
last_build_date = ""
last_weather_payload = {}

# Instantiate objects
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)

def publishWarnings(force=False):
  global last_build_date
  warnings_payload = getWarnings(AEMET_RSS, AEMET_AREA, REQUEST_TIMEOUT)
  if not warnings_payload:
    return

  warnings, build_date = warnings_payload
  if force or build_date != last_build_date:
    mqtt_client.publish("meteo/warnings", json.dumps(warnings))
    last_build_date = build_date

def publishWeather(force=False):
    global last_weather_payload
    weather_payload = getWeather(WHEATHER_API_KEY, WHEATHER_QUERY)
    if not weather_payload:
        return
    if force or weather_payload != last_weather_payload:
        mqtt_client.publish("meteo/weather", json.dumps(weather_payload))
        last_weather_payload = weather_payload

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("meteo/warnings/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "meteo/warnings/request")
  client.subscribe("meteo/weather/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "meteo/weather/request")

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
  if msg.topic == "meteo/warnings/request":
    publishWarnings(force=True)
  elif msg.topic == "meteo/weather/request":
    publishWeather(force=True)

def main():
  global last_heartbeat_timestamp
  global last_warnings_timestamp
  global last_weather_timestamp

  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if WHEATHER_API_KEY == "no_set": report("WHEATHER_API_KEY env vars no set")
  if WHEATHER_QUERY == "no_set": report("WHEATHER_QUERY env vars no set")
  if AEMET_RSS == "no_set": report("AEMET_RSS env vars no set")
  if AEMET_AREA == "no_set": report("AEMET_AREA env vars no set")

  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  # Connect to the MQTT broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)

  # Main loop
  while True:
    now = time.time()
    if now - last_warnings_timestamp > WARNINGS_INTERVAL:
      publishWarnings()
      last_warnings_timestamp = now

    if now - last_weather_timestamp > WEATHER_INTERVAL:
      publishWeather()
      last_weather_timestamp = now

    mqtt_client.publish("heartbeats", SERVICE)

    time.sleep(SLEEP_TIME)

# Main entry point
if __name__ == "__main__":
  main()
