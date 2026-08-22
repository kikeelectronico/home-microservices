import json
import logging
import os
import time

import paho.mqtt.client as mqtt

from esios import getEsiosIndicator


if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
ESIOS_API_KEY = os.environ.get("ESIOS_API_KEY", "no_set")
ENV = os.environ.get("ENV", "dev")

MQTT_PORT = 1883
SERVICE = "electricity-inflow-" + ENV
SLEEP_TIME = 10
ESIOS_INTERVAL = 300

last_esios_timestamp = 0
last_electricity_grid_payload = {}

mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)

def publishElectricityGrid(force=False):
  global last_electricity_grid_payload
  free_co2_generation_percentage_payload = getEsiosIndicator(ESIOS_API_KEY, 10033)
  if not free_co2_generation_percentage_payload:
    return

  if force or free_co2_generation_percentage_payload != last_electricity_grid_payload:
    mqtt_client.publish("electricity/grid", json.dumps(free_co2_generation_percentage_payload))
    last_electricity_grid_payload = free_co2_generation_percentage_payload


def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("electricity/grid/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "electricity/grid/request")


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


def on_message(client, userdata, msg):
  if msg.topic == "electricity/grid/request":
    publishElectricityGrid(force=True)


def main():
  global last_esios_timestamp

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )

  def report(message):
    print(message)
    exit()

  if MQTT_USER == "no_set":
    report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set":
    report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set":
    report("MQTT_HOST env vars no set")
  if ESIOS_API_KEY == "no_set":
    report("ESIOS_API_KEY env vars no set")

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)

  while True:
    if time.time() - last_esios_timestamp > ESIOS_INTERVAL:
      publishElectricityGrid()
      last_esios_timestamp = time.time()

    mqtt_client.publish("heartbeats", SERVICE)

    time.sleep(SLEEP_TIME)


if __name__ == "__main__":
  main()
