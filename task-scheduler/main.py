import paho.mqtt.client as mqtt
import time
import json
import logging

from constants import MQTT_PORT, TOPICS
from homeware import Homeware
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
tasks = []
settings = None
mqtt_client = None
homeware = None

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic, qos=1)

# Reconnect if MQTT disconnects unexpectedly
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

# Do tasks when a message is received
def on_message(client, userdata, msg):
  global tasks
  if msg.topic == "heartbeats/system":
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
    new_task = json.loads(msg.payload)
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

def main():
  global settings
  global mqtt_client
  global homeware
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
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)

  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  # Main loop
  mqtt_client.loop_start()
  while not stop_requested():
    wait_for_stop(1)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

# Main entry point
if __name__ == "__main__":
  main()
      
