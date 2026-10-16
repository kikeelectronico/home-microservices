import json
import logging
import time

import paho.mqtt.client as mqtt

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

def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe(STATUS_REQUEST_TOPIC, qos=1)
  logging.info("Subscribed to MQTT topic %s", STATUS_REQUEST_TOPIC)


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


def on_message(client, userdata, msg):
  if msg.topic == STATUS_REQUEST_TOPIC:
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
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
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
