import paho.mqtt.client as mqtt
import json
import os
import logging

from hue import Hue

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HUE_HOST = os.environ.get("HUE_HOST", "no_set")
HUE_TOKEN = os.environ.get("HUE_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = [
	"device/hue_1",
	"device/hue_2",
	"device/hue_3",
	"device/hue_4",
	"device/hue_5",
	"device/hue_6",
	"device/hue_7",
	"device/hue_8",
	"device/hue_9",
	"device/hue_10",
	"device/hue_11",
	"device/hue_12"
]
SERVICE = "hue-outbound-" + ENV

# Declare variables
service_id_device_id = {}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
hue = Hue(HUE_HOST, HUE_TOKEN)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
	if msg.topic in TOPICS:
		topic = msg.topic
		# Get service id
		hue_v1_device_id_key = topic.split("hue_")[1]
		hue_service_id = service_id_device_id.get(hue_v1_device_id_key)
		if not hue_service_id:
			logging.warning("No hue mapping for key %s on topic %s", hue_v1_device_id_key, topic)
			return
		# Validate payload
		try:
			payload = json.loads(msg.payload)
		except json.JSONDecodeError:
			logging.warning("Invalid JSON payload on %s: %r", topic, msg.payload)
			return
		if not isinstance(payload, dict):
			logging.warning("Invalid payload type on %s: %r", topic, payload)
			return
		# Extract payload data and generate hue status
		hue_status = {}
		if "on" in payload:
			if isinstance(payload["on"], bool):
				hue_status["on"] = {}
				hue_status["on"]["on"] = payload["on"]
			else:
				logging.warning("Invalid 'on' value on %s: %r", topic, payload.get("on"))
		if "brightness" in payload:
			brightness = payload.get("brightness")
			if isinstance(brightness, (int, float)) and 0 <= brightness <= 100:
				hue_status["dimming"] = {}
				hue_status["dimming"]["brightness"] = brightness
			else:
				logging.warning("Invalid 'brightness' value on %s: %r", topic, brightness)
		if "color" in payload:
			color = payload.get("color")
			temp_k = None
			if isinstance(color, dict):
				temp_k = color.get("temperatureK")
			if isinstance(temp_k, (int, float)) and temp_k > 0:
				hue_status["color_temperature"] = {}
				hue_status["color_temperature"]["mirek"] = round(1000000 / temp_k)
			else:
				logging.warning("Invalid 'color.temperatureK' value on %s: %r", topic, temp_k)
		# Alert if no status is created
		if not hue_status:
			logging.warning("No valid fields in payload on %s: %r", topic, payload)
			return
		# Call Hue Bridge
		hue.sendToHue(hue_service_id, hue_status)

# Main entry point
if __name__ == "__main__":
	# Check env vars
	def report(message):
		print(message)
		exit()
	if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
	if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
	if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
	if HUE_HOST == "no_set": report("HUE_HOST env vars no set")
	if HUE_TOKEN == "no_set": report("HUE_TOKEN env vars no set")

	# Declare the callback functions
	mqtt_client.on_message = on_message
	mqtt_client.on_connect = on_connect
	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
	logging.info("Starting " + SERVICE)

	# Get the v1 device ID to light service id map
	hue_devices = hue.getResource(resource="device")
	for hue_device in hue_devices:
		# Discart devices without v1 id
		if not hue_device.get("id_v1", False):
			continue
		# Get v1 device id
		hue_v1_device_id = hue_device["id_v1"].split("/")[2]
		# Map light services id to v1 device id
		for service in hue_device["services"]:
			if service.get("rtype", "none") == "light":
				service_id_device_id[hue_v1_device_id] = service["rid"]
	
	# Main loop
	mqtt_client.loop_forever()
 
