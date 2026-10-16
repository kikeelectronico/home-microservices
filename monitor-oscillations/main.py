import logging
import time
from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, OSCILLATION_THRESHOLD, PARAMS, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_status = {}


def handle_message(topic, payload):
  global last_status

  if topic == HEARTBEAT_TOPIC:
    for status_id in last_status:
      if last_status[status_id]["oscillating"]:
        if time.time() - last_status[status_id]["timestamp"] > OSCILLATION_THRESHOLD:
          mqtt_client.publish(f"oscillation/{status_id}", "reset")
          last_status[status_id]["counter"] = 0
          last_status[status_id]["oscillating"] = False
  else:
    topic = topic
    status_id = topic.split("device/")[1]
    payload = payload
    if last_status.get(status_id, None):
      if payload != last_status[status_id]["value"]:
        if time.time() - last_status[status_id]["timestamp"] < OSCILLATION_THRESHOLD:
          if last_status[status_id]["counter"] == 0:
            last_status[status_id]["counter"] = 1
          else:
            mqtt_client.publish(f"oscillation/{status_id}", "set")        
            last_status[status_id]["oscillating"] = True
        last_status[status_id]["value"] = payload
        last_status[status_id]["timestamp"] = time.time()
    else:
      last_status[status_id] = {
        "timestamp": time.time(),
        "value": payload,
        "counter": 0,
        "oscillating": False
      }

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
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=[HEARTBEAT_TOPIC] + [f"device/{topic}" for topic in PARAMS],
    message_handler=handle_message
  )
  mqtt_client.loop_start()
  while not stop_requested():
      # Send the heartbeat request and wait
      mqtt_client.publish(HEARTBEAT_TOPIC, "are-you-there")
      wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
