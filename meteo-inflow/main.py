import time
import logging
import json

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, REQUEST_TIMEOUT, SLEEP_TIME, WARNINGS_INTERVAL, WEATHER_INTERVAL
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


def handle_message(topic, payload):
  if topic == "meteo/warnings/request":
    publishWarnings(force=True)
  elif topic == "meteo/weather/request":
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
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=["meteo/warnings/request", "meteo/weather/request"],
    message_handler=handle_message
  )
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
