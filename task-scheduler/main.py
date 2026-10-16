import time
import json
import logging

from mqtt import set_mqtt_client
from constants import TOPICS
from homeware import Homeware
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
tasks = []
settings = None
mqtt_client = None
homeware = None


def handle_message(topic, payload):
  global tasks
  if topic == "heartbeats/system":
    for index, task in enumerate(tasks):
      if task["time"] < time.time():
        assert_pass = True
        for condition in task["asserts"]:
          if not homeware.get(condition["device_id"],condition["param"]) == condition["value"]:
            assert_pass = False
            break
        if assert_pass:
          homeware.execute(task["target"]["device_id"], task["target"]["param"], task["target"]["value"])
        del tasks[index]
  else:
    new_task = json.loads(payload)
    if new_task["action"] == "set":
      if "delta" in new_task:
        new_task["time"] = time.time() + new_task["delta"]      
      tasks.append(new_task)
      mqtt_client.publish("tasks/ack", json.dumps(new_task))
    elif new_task["action"] == "delete":
      for index, task in enumerate(tasks):
         if task["id"] == new_task["id"]:
            del tasks[index]
            mqtt_client.publish("tasks/ack", json.dumps(new_task))


# Main entry point
def main():
  global settings
  global mqtt_client
  global homeware
  # Register shutdown handlers
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
    subscriptions=TOPICS,
    message_handler=handle_message
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)

  # Main loop
  mqtt_client.loop_start()
  while not stop_requested():
    wait_for_stop(1)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
      
