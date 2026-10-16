import json
import logging

from mqtt import set_mqtt_client
from constants import MQTT_PORT, TOPICS
from ikea import Ikea
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
ikea = None


def handle_message(topic, payload):
	topic = topic
	try:
		payload = json.loads(payload)
	except json.JSONDecodeError:
		logging.warning("Invalid JSON payload on %s: %r", topic, payload)
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
	mqtt_client = set_mqtt_client(
		settings.mqtt_host,
		MQTT_PORT,
		settings.mqtt_user,
		settings.mqtt_pass,
		settings.service_id,
		subscriptions=TOPICS,
		message_handler=handle_message
	)
	ikea = Ikea(settings.ikea_host, settings.ikea_token)

	# Main loop
	mqtt_client.loop_start()
	while not stop_requested():
		wait_for_stop(1)
	# Clean shutdown
	logging.info("Disconnecting from the MQTT broker.")
	mqtt_client.loop_stop()
	mqtt_client.disconnect()
	logging.info("Shutdown completed.")
 
