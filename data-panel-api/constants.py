ENV_VARS = [
	"MQTT_HOST",
	"MQTT_PORT",
	"MQTT_USER",
	"MQTT_PASS"
]

SERVICE_NAME = "data-panel-api"

DEVICE_IDS = [
	"current001",
	"thermostat_livingroom",
	"fecf95fe-7cf3-4cc1-87bc-98e5669320f8_1",
	"ac_001",
	"e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
	"temperature_001",
	"df31ac85-be3f-48db-ab5e-483001f3ad27_1",
	"thermostat_bathroom",
	"9339195d-75c3-4fc1-aeac-03f8af899e40_1",
	"thermostat_dormitorio",
	"e6c2e2bd-5057-49bc-821f-a4b10e415ac6",
	"temperature_001",
	# "switch_at_home"
]

TOPICS = [
	"water/volume",
	"meteo/warnings",
	"meteo/weather",
	"electricity/grid",
	"internet/status",
	"fire/nearest",
	*[f"device/{device_id}" for device_id in DEVICE_IDS],
	"device/scene_ducha"
]
