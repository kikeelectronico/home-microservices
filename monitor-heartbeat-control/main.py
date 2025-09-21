import paho.mqtt.client as mqtt
import os
import time
import logging

from Homeware import Homeware

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = ["device/heartbeat"]
SERVICE = "monitor-heartbeat-control-" + ENV

# Declare variables
microservices_heartbeats = {}
devices_heartbeats = {}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
	if msg.topic == "device/heartbeat":
		# Save the timestamp when a device sends a heartbeat
		service = msg.payload
		if not service in devices_heartbeats:
				logging.info(service.decode("utf-8") + ": arriba")
		devices_heartbeats[service] = time.time()
		homeware.execute(service.decode("utf-8"), "online", True)

# Main entry point
if __name__ == "__main__":
	# Check env vars
	def report(message):
		print(message)
		exit()
	if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
	if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
	if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
	if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
	if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
    
	# Declare the callback functions
	mqtt_client.on_message = on_message
	mqtt_client.on_connect = on_connect
	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
	logging.info("Starting " + SERVICE)
	# Main loop
	mqtt_client.loop_forever()
 