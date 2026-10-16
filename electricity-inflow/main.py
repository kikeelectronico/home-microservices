import json
import logging
import time

import paho.mqtt.client as mqtt

from constants import ESIOS_INTERVAL, HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME
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


def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("electricity/grid/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "electricity/grid/request")


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
  if msg.topic == "electricity/grid/request":
    publishGrid(force=True)


def main():
  global last_grid_timestamp
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
