import json
import logging
import os
import time

import paho.mqtt.client as mqtt

from water import getWater


if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
ENV = os.environ.get("ENV", "dev")

MQTT_PORT = 1883
SERVICE = "water-inflow-" + ENV
SLEEP_TIME = 10
WATER_INTERVAL = 86400

last_water_timestamp = 0
last_water_payload = {}

mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)


def publishWater(force=False):
  global last_water_payload
  water_payload = getWater()
  if not water_payload:
    return

  if force or water_payload != last_water_payload:
    mqtt_client.publish("water", json.dumps(water_payload))
    last_water_payload = water_payload


def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("water/request", qos=1)
  logging.info("Subscribed to MQTT topic %s", "water/request")


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
  if msg.topic == "water/request":
    publishWater(force=True)


def main():
  global last_water_timestamp

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

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)

  while True:
    if time.time() - last_water_timestamp > WATER_INTERVAL:
      publishWater()
      last_water_timestamp = time.time()

    mqtt_client.publish("heartbeats", SERVICE)

    time.sleep(SLEEP_TIME)


if __name__ == "__main__":
  main()
