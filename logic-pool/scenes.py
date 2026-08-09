import time

BATHROOM_HUMIDITY_DELTA = 10

waiting_for_shower = False
initial_bathroom_humidity = 0
shower_informed = False
shower_initiated = False

# Set the shower scene
def shower(homeware, alert, topic, payload):
  global waiting_for_shower
  global shower_informed
  global shower_initiated
  global initial_bathroom_humidity
  if topic == "device/scene_ducha/enable":
    if payload:
      pass
      # alert.voice("Vale, preparo el baño.")
      # Start preparing the bathroom
      # homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 25)
      # homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
      # waiting_for_shower = True
      # initial_bathroom_humidity = homeware.get("thermostat_bathroom", "thermostatHumidityAmbient")
    else:
      # Return the bathroom to normal
      # alert.voice("Genial. Dejo de priorizar el baño.")
      # homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
      # homeware.execute("thermostat_bathroom", "thermostatMode", "off")
      # waiting_for_shower = False
      # shower_informed = False
      # shower_initiated = False
      if homeware.get("hue_sensor_14","on"):
        homeware.execute("hue_sensor_14","on",False)
  # Announce that the bathroom is ready to taking a shower
  # if topic == "device/thermostat_bathroom" and waiting_for_shower:
  #   if homeware.get("scene_winter", "enable"):
  #     if payload["thermostatTemperatureAmbient"] >= payload["thermostatTemperatureSetpoint"]:
  #       # waiting_for_shower = False
  #       if not shower_initiated and not shower_informed:
  #         alert.voice("El baño está listo.")
  #         shower_informed = True


def disableShowerScene(homeware, alert, topic, payload):
  global waiting_for_shower
  global shower_informed
  global shower_initiated
  global initial_bathroom_humidity
  if topic == "device/thermostat_bathroom/thermostatHumidityAmbient":
    # if initial_bathroom_humidity == 0: initial_bathroom_humidity = homeware.get("thermostat_bathroom", "thermostatHumidityAmbient")
    if waiting_for_shower:
      if homeware.get("thermostat_bathroom", "thermostatHumidityAmbient") > (initial_bathroom_humidity + BATHROOM_HUMIDITY_DELTA):
        shower_initiated = True

  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/occupancy":
    if payload == "OCCUPIED":
      if homeware.get("scene_ducha", "enable"):
        if shower_initiated:
          homeware.execute("scene_ducha", "enable", False)
          waiting_for_shower = False
          shower_informed = False
          shower_initiated = False
          alert.voice("Veo que ya te has duchado. Dejo de priorizar el baño.")

