import json
import logging
import time


from water import getWater
from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, SLEEP_TIME, WATER_INTERVAL
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_volume_timestamp = 0
last_volume_payload = {}


def publishVolume(force=False):
  global last_volume_payload
  water_payload = getWater()
  if not water_payload:
    return

  if force or water_payload != last_volume_payload:
    mqtt_client.publish("water/volume", json.dumps(water_payload))
    last_volume_payload = water_payload




def handle_message(topic, payload):
  if topic == "water/volume/request":
    publishVolume(force=True)


# Main entry point
def main():
  global last_volume_timestamp
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
    subscriptions=["water/volume/request"],
    message_handler=handle_message
  )
  mqtt_client.loop_start()

  while not stop_requested():
    if time.time() - last_volume_timestamp > WATER_INTERVAL:
      publishVolume()
      last_volume_timestamp = time.time()

    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
