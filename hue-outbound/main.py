import paho.mqtt.client as mqtt
import json
import logging

from constants import MQTT_PORT
from hue import Hue
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
service_id_device_id = {}
topics = []
settings = None
mqtt_client = None
hue = None

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in topics:
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

# Do tasks when a message is received
def on_message(client, userdata, msg):
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
	hue_service_properties = {}
	if "on" in payload:
		homeware_on = payload.get("on")
		if isinstance(homeware_on, bool):
			hue_service_properties["on"] = {}
			hue_service_properties["on"]["on"] = homeware_on
		else:
			logging.warning("Invalid on value on %s: %r", topic, payload.get("on"))
	if "brightness" in payload:
		homeware_brightness = payload.get("brightness")
		if isinstance(homeware_brightness, (int, float)) and 0 <= homeware_brightness <= 100:
			hue_service_properties["dimming"] = {}
			hue_service_properties["dimming"]["brightness"] = homeware_brightness
		else:
			logging.warning("Invalid brightness value on %s: %r", topic, homeware_brightness)
	if "color" in payload:
		homeware_color = payload.get("color")
		temp_k = None
		if isinstance(homeware_color, dict):
			temp_k = homeware_color.get("temperatureK")
		if isinstance(temp_k, (int, float)) and temp_k > 0:
			hue_service_properties["color_temperature"] = {}
			hue_service_properties["color_temperature"]["mirek"] = round(1000000 / temp_k)
		else:
			logging.warning("Invalid color.temperatureK value on %s: %r", topic, temp_k)
	if "currentToggleSettings" in payload:
		homeware_current_toggle_settings = payload.get("currentToggleSettings")
		homeware_emergency_toggle = None
		if isinstance(homeware_current_toggle_settings, dict):
			homeware_emergency_toggle = homeware_current_toggle_settings.get("emergencia")
		if isinstance(homeware_emergency_toggle, bool):
			if homeware_emergency_toggle:
				hue_service_properties = {
					"on": {
						"on": True
					},
					"dimming": {
						"brightness": 100
					},
					"effects": {
						"status": "cosmos"
					},
					"effects_v2": {
						"action": {
							"effect": "cosmos",
							"parameters": {
								"color": {
								"xy": {
									"x": 0.6845,
									"y": 0.3064
								}
								},
								"speed": 0.6151
							}
						}
					},
					"color": {
						"xy": {
							"x": 0.6845,
							"y": 0.3064
						}
					}
				}
			else:
				hue_current_service = hue.getService("light", hue_service_id)
				if "effects_v2" in hue_current_service:
					hue_current_effects_v2_property = hue_current_service["effects_v2"]
					if hue_current_effects_v2_property["status"]["effect"] != "no_effect":
						hue_service_properties = {
							"on": {
								"on": True
							},
							"dimming": {
								"brightness": 22
							},
							"effects": {
								"status": "no_effect"
							},
							"effects_v2": {
								"status": {
									"effect": "no_effect",
									"parameters": None
								}
							},
							"color_temperature": {
								"mirek": round(1000000 / 2200),
								"mirek_valid": True
							}
						}
		else:
			logging.warning("Invalid currentToggleSettings.emergencia value on %s: %r", topic, temp_k)
	# Alert if no status is created
	if not hue_service_properties:
		logging.warning("No valid fields in payload on %s: %r", topic, payload)
		return
	# Call Hue Bridge
	hue.updateLightService(hue_service_id, hue_service_properties)

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
	hue = Hue(settings.hue_host, settings.hue_token)

	# Get the v1 device ID to light service id map
	hue_devices = hue.getServices(type="device")
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
				topics.append("device/hue_" + hue_v1_device_id)

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
 
