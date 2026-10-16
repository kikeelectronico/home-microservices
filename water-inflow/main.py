import json
import logging
import time

import paho.mqtt.client as mqtt

from water import getWater
from constants import HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME, WATER_INTERVAL
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


def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("water/volume/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "water/volume/request")


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
  if msg.topic == "water/volume/request":
    publishVolume(force=True)


def main():
  global last_volume_timestamp
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
