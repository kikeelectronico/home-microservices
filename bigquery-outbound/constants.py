ENV_VARS = [
	"MQTT_HOST",
	"MQTT_USER",
	"MQTT_PASS",
	"DEVICE_DDBB"
]

MQTT_PORT = 1883
POWER_CONSTANT = 35
SERVICE_NAME = "bigquery-outbound"

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
