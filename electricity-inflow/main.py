import json
import logging
import time


from mqtt import set_mqtt_client
from constants import ESIOS_INTERVAL, HEARTBEAT_TOPIC, SLEEP_TIME
from esios import getEsiosIndicator
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_grid_timestamp = 0
last_grid_payload = {}

def publishGrid(force=False):
  global last_grid_payload
  free_co2_generation_percentage_payload = getEsiosIndicator(settings.esios_api_key, 10033)
  if not free_co2_generation_percentage_payload:
    return

  if force or free_co2_generation_percentage_payload != last_grid_payload:
    mqtt_client.publish("electricity/grid", json.dumps(free_co2_generation_percentage_payload))
    last_grid_payload = free_co2_generation_percentage_payload




def handle_message(topic, payload):
  if topic == "electricity/grid/request":
    publishGrid(force=True)


def main():
  global last_grid_timestamp
  global settings
  global mqtt_client

  # Register shutdown handlers
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()

  logging.basicConfig(
    level=logging.INFO,
    format=(
      "%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
      if settings.env == "dev"
      else "%(message)s"
    )
  )
  logging.info("Starting %s", settings.service_id)

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=["electricity/grid/request"],
    message_handler=handle_message
  )
  mqtt_client.loop_start()

  while not stop_requested():
    if time.time() - last_grid_timestamp > ESIOS_INTERVAL:
      publishGrid()
      last_grid_timestamp = time.time()

    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")


if __name__ == "__main__":
  main()
