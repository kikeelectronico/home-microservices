ENV_VARS = [
	"MQTT_HOST",
	"MQTT_PORT",
	"MQTT_USER",
	"MQTT_PASS",
	"HOMEWARE_API_URL",
	"HOMEWARE_API_KEY"
]

SLEEP_TIME = 10
SERVICE_NAME = "monitor-cause-effect"
HEARTBEAT_TOPIC = "heartbeats"

RULES = [
	{
		"device_id": "interruptor_prueba",
		"param": "on",
		"value": True,
		"reset_value": False,
		"effects": [
			{
				"device_id": "bombilla_prueba",
				"param": "on",
				"operator": "==",
				"value": True 
			}
		]
	}
]