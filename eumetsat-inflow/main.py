import json
import logging
import time


from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, NEAREST_FIRE_INTERVAL, SLEEP_TIME
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



def handle_message(topic, payload):
  if topic == "fire/nearest/request":
    publishNearestFire(force=True)


def main():
  global last_nearest_fire_timestamp
  global settings
  global mqtt_client
  
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
    subscriptions=["fire/nearest/request"],
    message_handler=handle_message
  )
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
