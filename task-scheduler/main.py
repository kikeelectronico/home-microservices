import paho.mqtt.client as mqtt
import time
import os
import json
import logging

from homeware import Homeware

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
WHEATHER_API_KEY = os.environ.get("WHEATHER_API_KEY", "no_set")
WHEATHER_QUERY = os.environ.get("WHEATHER_QUERY", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = [ "tasks", "heartbeats/request" ]
SERVICE = "task-scheduler-" + ENV

# Declare variables
last_heartbeat_timestamp = 0
tasks = []

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, SERVICE)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
  global tasks
  if msg.topic == "heartbeats/request":
    # Send heartbeat
    mqtt_client.publish("heartbeats", SERVICE)
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
  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if WHEATHER_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if WHEATHER_QUERY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  
  logging.info("Starting " + SERVICE)

  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  # Main loop
  mqtt_client.loop_forever()

# Main entry point
if __name__ == "__main__":
  main()
      
