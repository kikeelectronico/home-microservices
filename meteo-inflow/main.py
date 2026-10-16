import paho.mqtt.client as mqtt
import time
import logging
import json

from constants import HEARTBEAT_TOPIC, MQTT_PORT, REQUEST_TIMEOUT, SLEEP_TIME, WARNINGS_INTERVAL, WEATHER_INTERVAL
from weather import getWeather
from weather_warnings import getWarnings
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_warnings_timestamp = 0
last_weather_timestamp = 0
last_warnings_payload = {}
last_weather_payload = {}
settings = None
mqtt_client = None

def publishWarnings(force=False):
  global last_warnings_payload
  warnings_payload = getWarnings(settings.aemet_rss, settings.aemet_area, REQUEST_TIMEOUT)
  if not warnings_payload:
    return

  if force or warnings_payload != last_warnings_payload:
    mqtt_client.publish("meteo/warnings", json.dumps(warnings_payload))
    last_warnings_payload = warnings_payload

def publishWeather(force=False):
    global last_weather_payload
    weather_payload = getWeather(settings.wheather_api_key, settings.wheather_query)
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
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        wait_for_stop(5)

# Do tasks when a message is received
def on_message(client, userdata, msg):
  if msg.topic == "meteo/warnings/request":
    publishWarnings(force=True)
  elif msg.topic == "meteo/weather/request":
    publishWeather(force=True)

def main():
  global last_warnings_timestamp
  global last_weather_timestamp
  global settings
  global mqtt_client

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )

  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting %s", settings.service_id)

  # Instantiate objects
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )

  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  # Connect to the MQTT broker
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()

  # Main loop
  while not stop_requested():
    now = time.time()
    if now - last_warnings_timestamp > WARNINGS_INTERVAL:
      publishWarnings()
      last_warnings_timestamp = now

    if now - last_weather_timestamp > WEATHER_INTERVAL:
      publishWeather()
      last_weather_timestamp = now

    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    wait_for_stop(SLEEP_TIME)

  # Clean shutdown
  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

# Main entry point
if __name__ == "__main__":
  main()
