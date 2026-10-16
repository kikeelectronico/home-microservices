import time
import paho.mqtt.client as mqtt
from google.cloud import bigquery
import logging
import json
from constants import MQTT_PORT, POWER_CONSTANT, TOPICS
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_value = {}

# Create vars for objects
settings = None
mqtt_client = None

# Instantiate objects
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
		while not stop_requested():
			try:
				client.reconnect()
				logging.info("Reconnected to MQTT broker")
				break
			except Exception as exc:
				logging.warning("Reconnect failed: %s", exc)
				wait_for_stop(5)

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
		except (IndexError, KeyError, TypeError) as exc:
			logging.warning("Invalid message structure on %s: %s", topic, exc)
			return
		try:
			for state in states:
				# Insert the data
				query_job = bigquery_client.query(
					"""
						INSERT INTO {}
						(time, device_id, param, value, type)
						VALUES ({},"{}","{}","{}", "{}");
					""".format(settings.device_ddbb, ts, device_id, state["param"], str(state["value"]), state["value"].__class__.__name__)
				)
				query_job.result()
			# Update last_value
			last_value[topic] = payload
		except Exception as exc:
			logging.warning(
				"Fail to insert state into BigQuery on %s: device_id=%s param=%s value=%r error=%s",
				topic,
				device_id,
				state.get("param"),
				state.get("value"),
				exc
			)

# Main entry point
if __name__ == "__main__":
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
	)

  	# Register shutdown handlers
	register_shutdown_handlers()

	# Load settings
	settings = Settings()
	settings.load_settings()
	logging.info("Starting %s", settings.service_id)

	mqtt_client = mqtt.Client(
		mqtt.CallbackAPIVersion.VERSION2,
		client_id=settings.service_id,
		protocol=mqtt.MQTTv5
	)

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
 
