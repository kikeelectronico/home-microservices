import paho.mqtt.client as mqtt
import json
import logging

from constants import MQTT_PORT, TOPICS
from ikea import Ikea
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
ikea = None

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic, qos=1)

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
	if rc != 0:
		logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)

# Do tasks when a message is received
def on_message(client, userdata, msg):
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
	ikea = Ikea(settings.ikea_host, settings.ikea_token)

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
	# Clean shutdown
	logging.info("Disconnecting from the MQTT broker.")
	mqtt_client.loop_stop()
	mqtt_client.disconnect()
	logging.info("Shutdown completed.")
 
