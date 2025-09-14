import requests
import paho.mqtt.client as mqtt
import json
import os
import logging

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
POWER_CONSTANT = 35
TOPICS = [
	"heartbeats/request",
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

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)

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
			hue_id = topic.split("hue_")[1]
			hue_status = {}
			if "on" in payload:
				hue_status["on"] = payload["on"]
			if "brightness" in payload:
				hue_status["bri"] = round((payload["brightness"]/100)*254)
			if "color" in payload:
				hue_status["ct"] = round(1000000/payload["color"]["temperatureK"])
			sendToHue(hue_id, hue_status)

# Send an update request to Hue bridge API
def sendToHue(hue_id, hue_status):
	try:
		url = "http://" + HUE_HOST + "/api/" +	HUE_TOKEN + "/lights/" + hue_id + "/state"
		headers = {
			"Content-Type": "application/json"
		}
		response = requests.put(url, data = json.dumps(hue_status), headers = headers)
		if not response.status_code == 200:
			logging.warning("Fail to update to Hue Bridge lights. Status code: " + str(response.status_code))
	except (requests.ConnectionError, requests.Timeout) as exception:
		logging.warning("Fail to update Hue Bridge lights. Conection error.")


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
	# Main loop
	mqtt_client.loop_forever()
 