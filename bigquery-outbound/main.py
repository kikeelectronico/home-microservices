import time
import paho.mqtt.client as mqtt
import os
from google.cloud import bigquery
import logging

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
DEVICE_DDBB = os.environ.get("DEVICE_DDBB", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
POWER_CONSTANT = 35
TOPICS = [
	"heartbeats/request",
	"device/current001/brightness",
	"device/thermostat_livingroom/thermostatTemperatureAmbient",
	"device/thermostat_livingroom/thermostatHumidityAmbient",
	"device/thermostat_livingroom/thermostatMode",
	"device/thermostat_bathroom/thermostatTemperatureAmbient",
	"device/thermostat_bathroom/thermostatHumidityAmbient",
	"device/thermostat_dormitorio/thermostatTemperatureAmbient",
	"device/thermostat_dormitorio/thermostatHumidityAmbient",
	"device/temperature_001/temperatureAmbientCelsius",
	"device/temperature_001/humidityAmbientPercent",
	"device/hue_5/on",
	"device/hue_5/brightness",
	"device/scene_awake/enable",
	"device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness",
	"device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
	"device/e6c2e2bd-5057-49bc-821f-a4b10e415ac6/openPercent"
]
SERVICE = "bigquery-outbound-" + ENV

# Declare variables
last_value = {}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
bigquery_client = bigquery.Client()

# Change the type of the payload
def typifyPayload(topic, payload):
	if "heartbeats" in topic:
		return payload
	elif "Temperature" in topic:
		return float(payload)
	elif "temperature" in topic:
		return float(payload)
	else:
		return int(payload)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic)

# Do a tasks when a message is received
def on_message(client, userdata, msg):
	global last_value
	# Rename variables
	topic = msg.topic
	payload = typifyPayload(topic, msg.payload)
	# The request depends on the device
	if topic == "heartbeats/request":
		mqtt_client.publish("heartbeats", SERVICE)
	else:
		if payload != last_value.setdefault(topic, 0):
			# Prepare the data
			ts = int(time.time())
			device_id = topic.split("/")[1]
			param = topic.split("/")[2] if not "current001" in topic else "current"
			value = payload if not "current001" in topic else payload * POWER_CONSTANT
			# Insert the data
			bigquery_client.query(
				"""
					INSERT INTO {}
					(time, device_id, param, value, type)
					VALUES ({},"{}","{}","{}", "{}");
				""".format(DEVICE_DDBB, ts, device_id, param, str(value), value.__class__.__name__)
			)
			# Update last_value
			last_value[topic] = payload

# Main entry point
if __name__ == "__main__":
	# Check env vars
	def report(message):
		print(message)
		exit()
	if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
	if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
	if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
	if DEVICE_DDBB == "no_set": report("DEVICE_DDBB env vars no set")
		
	# Declare the callback functions
	mqtt_client.on_message = on_message
	mqtt_client.on_connect = on_connect
  	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
	logging.info("Starting " + SERVICE)
  	# Main loop
	mqtt_client.loop_forever()
 