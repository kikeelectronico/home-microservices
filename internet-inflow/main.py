import json
import logging
import time


from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME, STATUS_REQUEST_TOPIC, STATUS_TOPIC
from Internet import getInternetStatus
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_status = {}


def publishStatus(force=False):
  global last_status
  internet_status = getInternetStatus()

  if force or internet_status != last_status:
    mqtt_client.publish(STATUS_TOPIC, json.dumps(internet_status))
    last_status = internet_status



def handle_message(topic, payload):
  if topic == STATUS_REQUEST_TOPIC:
    publishStatus(force=True)


def main():
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
    MQTT_PORT,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=[STATUS_REQUEST_TOPIC],
    message_handler=handle_message
  )
  mqtt_client.loop_start()

  while not stop_requested():
    publishStatus()

    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")


if __name__ == "__main__":
  main()
