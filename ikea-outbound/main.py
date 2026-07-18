import paho.mqtt.client as mqtt
import json
import os
import logging
import time

from ikea import Ikea

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
TOPICS = [
	"device/b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
	"device/fc553d8b-1f45-4337-84ab-5c80a84e61ff_1",
	"device/df31ac85-be3f-48db-ab5e-483001f3ad27_1",
	"device/9339195d-75c3-4fc1-aeac-03f8af899e40_1",
	"device/fecf95fe-7cf3-4cc1-87bc-98e5669320f8_1",
]
SERVICE = "ikea-outbound-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(
	mqtt.CallbackAPIVersion.VERSION2,
	client_id=SERVICE,
	protocol=mqtt.MQTTv5
)
ikea = Ikea(IKEA_HOST, IKEA_TOKEN)

# Subscribe to topics on connect
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

# Do tasks when a message is received
def on_message(client, userdata, msg):
	if msg.topic in TOPICS:
		topic = msg.topic
		try:
			payload = json.loads(msg.payload)
		except json.JSONDecodeError:
			logging.warning("Invalid JSON payload on %s: %r", topic, msg.payload)
			return
		if not isinstance(payload, dict):
			logging.warning("Invalid payload type on %s: %r", topic, payload)
			return
		ikea_id = topic.split("/")[1]
		# Air purifier
		if "currentModeSettings" in payload and "currentFanSpeedSetting" in payload:
			homeware_current_mode_settings = payload.get("currentModeSettings")
			if not isinstance(homeware_current_mode_settings, dict):
				logging.warning("Invalid 'currentModeSettings' value on %s: %r", topic, homeware_current_mode_settings)
				return
			homeware_mode = homeware_current_mode_settings.get("Modo")
			if not homeware_mode:
				logging.warning("Missing 'currentModeSettings.Modo' on %s: %r", topic, homeware_current_mode_settings)
				return
			match homeware_mode:
				case "Apagado":
					ikea.updateDeviceAttribute(ikea_id, "fanMode", "off")
				case "Automático":
					ikea.updateDeviceAttribute(ikea_id, "fanMode", "auto")
				case "Manual":
					ikea.updateDeviceAttribute(ikea_id, "fanMode", "on")
					match payload["currentFanSpeedSetting"]:
						case "Baja":
							ikea.updateDeviceAttribute(ikea_id, "motorState", 10)
						case "Media":
							ikea.updateDeviceAttribute(ikea_id, "motorState", 30)
						case "Alta":
							ikea.updateDeviceAttribute(ikea_id, "motorState", 50)
					ikea.updateDeviceAttribute(ikea_id, "fanMode", "on")
		else:
			if "on" in payload:
				ikea.updateDeviceAttribute(ikea_id, "isOn", payload["on"])
		
		


# Main entry point
if __name__ == "__main__":
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
	)
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
	mqtt_client.on_disconnect = on_disconnect
	# Connect to the mqtt broker
	mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
	mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
	mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
	logging.info("Starting " + SERVICE)
	# Main loop
	mqtt_client.loop_forever()
 
