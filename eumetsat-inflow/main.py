import json
import logging
import os
import time

import paho.mqtt.client as mqtt

from eumetsat import getNearestFire

if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
EUMETSAT_CONSUMER_KEY = os.environ.get("EUMETSAT_CONSUMER_KEY", "no_set")
EUMETSAT_CONSUMER_SECRET = os.environ.get("EUMETSAT_CONSUMER_SECRET", "no_set")
REFERENCE_LAT = float(os.environ.get("REFERENCE_LAT", "no_set"))
REFERENCE_LON = float(os.environ.get("REFERENCE_LON", "no_set"))
BOUNDING_BOX = os.environ.get("BOUNDING_BOX", "-6.18, 39.13, -2.67, 41.36")
ENV = os.environ.get("ENV", "dev")

MQTT_PORT = 1883
SERVICE = "eumetsat-inflow-" + ENV
SLEEP_TIME = 30
NEAREST_FIRE_INTERVAL = 1800

last_nearest_fire_timestamp = 0
last_nearest_fire_payload = {}

mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)


def publishNearestFire(force=False):
  global last_nearest_fire_payload    
  nearest_fire = getNearestFire(
    consumer_key=EUMETSAT_CONSUMER_KEY,
    consumer_secret=EUMETSAT_CONSUMER_SECRET,
    ref_lat=REFERENCE_LAT,
    ref_lon=REFERENCE_LON,
    bbox=BOUNDING_BOX
  )
  if not nearest_fire:
    return
  
  if force or nearest_fire != last_nearest_fire_payload:
    mqtt_client.publish("fire/nearest", json.dumps(nearest_fire))
    last_nearest_fire_payload = nearest_fire

def on_connect(client, userdata, flags, rc, properties):
  logging.info(f"Conectado al broker MQTT (rc={rc})")
  client.subscribe("fire/nearest/request", qos=1)
  logging.info(f"Suscrito al topic MQTT 'fire/nearest/request'")


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
  if msg.topic == "fire/nearest/request":
    publishNearestFire(force=True)


def main():
  global last_nearest_fire_timestamp
  
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  
  def report(message):
    print(message)
    exit(1)

  if MQTT_USER == "no_set":
    report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set":
    report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set":
    report("MQTT_HOST env vars no set")
  if EUMETSAT_CONSUMER_KEY == "no_set":
    report("EUMETSAT_CONSUMER_KEY env vars no set")
  if EUMETSAT_CONSUMER_SECRET == "no_set":
    report("EUMETSAT_CONSUMER_SECRET env vars no set")
  if REFERENCE_LAT == "no_set":
    report("REFERENCE_LAT env vars no set")
  if REFERENCE_LON == "no_set":
    report("REFERENCE_LON env vars no set")

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)
  
  while True:
    if time.time() - last_nearest_fire_timestamp > NEAREST_FIRE_INTERVAL:
      publishNearestFire()
      last_nearest_fire_timestamp = time.time()

    mqtt_client.publish("heartbeats", SERVICE)

    time.sleep(SLEEP_TIME)

if __name__ == "__main__":
  main()