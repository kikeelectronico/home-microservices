import time
import paho.mqtt.client as mqtt
import os
from google.cloud import bigquery
import logging
import json

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
	"device/current001/brightness",
	"device/thermostat_livingroom/thermostatTemperatureAmbient",
	"device/thermostat_livingroom/thermostatHumidityAmbient",
	"device/thermostat_livingroom/thermostatMode",
	"device/thermostat_livingroom/currentSensorStateData",
	"device/df31ac85-be3f-48db-ab5e-483001f3ad27_1/currentSensorStateData",
	"device/thermostat_bathroom/thermostatTemperatureAmbient",
	"device/thermostat_bathroom/thermostatHumidityAmbient",
	"device/thermostat_dormitorio/thermostatTemperatureAmbient",
	"device/thermostat_dormitorio/thermostatHumidityAmbient",
	"device/temperature_001/temperatureAmbientCelsius",
	"device/temperature_001/humidityAmbientPercent",
	"device/hue_17/on",
	"device/hue_17/brightness",
	"device/scene_awake/enable",
	"device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness",
	"device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
	"device/e6c2e2bd-5057-49bc-821f-a4b10e415ac6/openPercent"
]
SERVICE = "bigquery-outbound-" + ENV

# Declare variables
last_value = {}

# Instantiate objects
mqtt_client = mqtt.Client(
	mqtt.CallbackAPIVersion.VERSION2,
	client_id=SERVICE,
	protocol=mqtt.MQTTv5
)
bigquery_client = bigquery.Client()

# Change the type of the payload
def typifyPayload(topic, payload):
	if "heartbeats" in topic:
		return payload
	elif "Temperature" in topic:
		return float(payload)
	elif "temperature" in topic:
		return float(payload)
	elif "currentSensorStateData" in topic:
		return json.loads(payload.replace("'", '"'))
	else:
		return int(payload)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic, qos=1)

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
	if rc != 0:
		logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
		while True:
			try:
				client.reconnect()
				logging.info("Reconnected to MQTT broker")
				break
			except Exception as exc:
				logging.warning("Reconnect failed: %s", exc)
				time.sleep(5)

# Do a tasks when a message is received
def on_message(client, userdata, msg):
	global last_value
	# Rename variables
	topic = msg.topic
	try:
		payload = typifyPayload(topic, msg.payload.decode("utf-8"))
	except (ValueError, TypeError, json.JSONDecodeError) as exc:
		logging.warning("Invalid payload on %s: %r (%s)", topic, msg.payload, exc)
		return
	# The request depends on the device
	if payload != last_value.setdefault(topic, 0):
		try:
			# Prepare the data
			ts = int(time.time())
			device_id = topic.split("/")[1]
			states = []
			if "current001" in topic:
				states.append(
					{
						"param": "current",
						"value": payload * POWER_CONSTANT
					}
				)
			elif "currentSensorStateData" in topic:
				if not isinstance(payload, list):
					logging.warning("Invalid currentSensorStateData payload type on %s: %r", topic, payload)
					return
				for sensor in payload:
					if not isinstance(sensor, dict):
						logging.warning("Invalid sensor payload on %s: %r", topic, sensor)
						return
					if "name" not in sensor or "rawValue" not in sensor:
						logging.warning("Missing sensor fields on %s: %r", topic, sensor)
						return
					states.append(
						{
							"param": sensor["name"],
							"value": sensor["rawValue"]
						}
					)
			else:
				states.append(
					{
						"param": topic.split("/")[2],
						"value": payload
					}
				)
			for state in states:
				# Insert the data
				bigquery_client.query(
					"""
						INSERT INTO {}
						(time, device_id, param, value, type)
						VALUES ({},"{}","{}","{}", "{}");
					""".format(DEVICE_DDBB, ts, device_id, state["param"], str(state["value"]), state["value"].__class__.__name__)
				)
			# Update last_value
			last_value[topic] = payload
		except (IndexError, KeyError, TypeError) as exc:
			logging.warning("Invalid message structure on %s: %s", topic, exc)

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
	mqtt_client.on_disconnect = on_disconnect
  	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
	logging.info("Starting " + SERVICE)
  	# Main loop
	mqtt_client.loop_forever()
 
