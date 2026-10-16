import json
import logging
import time

import paho.mqtt.client as mqtt

from constants import HEARTBEAT_TOPIC, MQTT_PORT, NEAREST_FIRE_INTERVAL, SLEEP_TIME
from eumetsat import getNearestFire
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_nearest_fire_timestamp = 0
last_nearest_fire_payload = {}

def publishNearestFire(force=False):
  global last_nearest_fire_payload    
  nearest_fire = getNearestFire(
    consumer_key=settings.eumetsat_consumer_key,
    consumer_secret=settings.eumetsat_consumer_secret,
    ref_lat=float(settings.reference_lat),
    ref_lon=float(settings.reference_lon),
    bbox=settings.bounding_box
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
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        wait_for_stop(5)


def on_message(client, userdata, msg):
  if msg.topic == "fire/nearest/request":
    publishNearestFire(force=True)


def main():
  global last_nearest_fire_timestamp
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
    if time.time() - last_nearest_fire_timestamp > NEAREST_FIRE_INTERVAL:
      publishNearestFire()
      last_nearest_fire_timestamp = time.time()

    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
