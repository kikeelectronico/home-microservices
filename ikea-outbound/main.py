import requests
import paho.mqtt.client as mqtt
import json
import os


from ikea import Ikea
from logger import Logger

import urllib3
urllib3.disable_warnings()

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
IKEA_HOST = os.environ.get("IKEA_HOST", "no_set")
IKEA_TOKEN = os.environ.get("IKEA_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
POWER_CONSTANT = 35
TOPICS = [
	"heartbeats/request",
	"device/b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
	"device/fc553d8b-1f45-4337-84ab-5c80a84e61ff_1",
]
SERVICE = "ikea-outbound-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
ikea = Ikea(IKEA_HOST, IKEA_TOKEN, logger)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
	if msg.topic in TOPICS:
		if msg.topic == "heartbeats/request":
			mqtt_client.publish("heartbeats", SERVICE)
		else:
			topic = msg.topic
			payload = json.loads(msg.payload)
			ikea_id = topic.split("/")[1]
			if "on" in payload:
				ikea.setDevice(ikea_id, "isOn", payload["on"])


# Main entry point
if __name__ == "__main__":
	# Check env vars
	def report(message):
		print(message)
		exit()

	if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
	if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
	if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
	if IKEA_HOST == "no_set": report("IKEA_HOST env vars no set")
	if IKEA_TOKEN == "no_set": report("IKEA_TOKEN env vars no set")

	# Declare the callback functions
	mqtt_client.on_message = on_message
	mqtt_client.on_connect = on_connect
	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
	logger.log("Starting " + SERVICE , severity="INFO")
	# Main loop
	mqtt_client.loop_forever()
 