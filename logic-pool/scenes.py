import time

DELAY_BETWEEN_POWER_ALERTS = 40
BATHROOM_HUMIDITY_DELTA = 10

power_alert_counter = 0
last_power_check = 0
waiting_for_shower = False
initial_bathroom_humidity = 0
shower_initiated = False

# Set dim scene
def dim(homeware, topic, payload):
  if topic == "device/scene_dim/enable":
    if payload:
      # Adjust bedroom lights
      if homeware.get("hue_6", "on"):
        homeware.execute("rgb003", "on", True)
        homeware.execute("hue_6", "on", False)
      # Adjust bathroom lights
      devices_ids = ["hue_2","hue_3"]
      for device_id in devices_ids:
        homeware.execute(device_id, "color", {"temperatureK": 3000})
        homeware.execute(device_id, "brightness", 20)
      if homeware.get("light001", "on"):
        homeware.execute("hue_sensor_2", "on", True)
        homeware.execute("light001", "on", False)
      # Adjust hall light
      devices_ids = ["hue_7"]
      for device_id in devices_ids:
        homeware.execute(device_id, "brightness", 30) 
      # Adjust RGB strips
      devices_ids = ["rgb002", "rgb003"]
      color = {
        "spectrumRGB": 16729344,
        "spectrumRgb": 16729344
      }
      for device_id in devices_ids:
        homeware.execute(device_id, "color", color)
    else:
      # Adjust bedroom lights
      if homeware.get("rgb003", "on"):
        homeware.execute("hue_6", "on", True)
        homeware.execute("rgb003", "on", False)
      # Adjust bathroom lights
      devices_ids = ["hue_2","hue_3"]
      for device_id in devices_ids:
        homeware.execute(device_id, "color", {"temperatureK": 5000})
        homeware.execute(device_id, "brightness", 80)
      if homeware.get("hue_sensor_2", "on"):
        homeware.execute("light001", "on", True)
        homeware.execute("hue_sensor_2", "on", False)
      # Adjust hall light      
      devices_ids = ["hue_7"]
      for device_id in devices_ids:
        homeware.execute(device_id, "brightness", 100)
      # Adjust RGB strips
      devices_ids = ["rgb002", "rgb003"]
      color = {
        "spectrumRGB": 16741656,
        "spectrumRgb": 16741656
      }
      for device_id in devices_ids:
        homeware.execute(device_id, "color", color)

# Set the shower scene
def shower(homeware, alert, topic, payload):
  global waiting_for_shower
  global shower_initiated
  global initial_bathroom_humidity
  if topic == "device/scene_ducha/enable":
    if payload:
      alert.voice("Vale, preparo el baño.")
      # Start preparing the bathroom
      homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 25)
      homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
      waiting_for_shower = True
      initial_bathroom_humidity = homeware.get("thermostat_bathroom", "thermostatHumidityAmbient")
    else:
      # Return the bathroom to normal
      alert.voice("Genial. Dejo de priorizar el baño.")
      homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
      homeware.execute("thermostat_bathroom", "thermostatMode", "off")
      waiting_for_shower = False
      shower_initiated = False
      if homeware.get("hue_sensor_14","on"):
        homeware.execute("hue_sensor_14","on",False)
  # Announce that the bathroom is ready to taking a shower
  if topic == "device/thermostat_bathroom" and waiting_for_shower:
    if homeware.get("scene_winter", "enable"):
      if payload["thermostatTemperatureAmbient"] >= payload["thermostatTemperatureSetpoint"]:
        waiting_for_shower = False
        alert.voice("El baño está listo.")


def disableShowerScene(homeware, alert, topic, payload):
  global waiting_for_shower
  global shower_initiated
  global initial_bathroom_humidity
  if topic == "device/thermostat_bathroom/thermostatHumidityAmbient":
    if initial_bathroom_humidity == 0: initial_bathroom_humidity = homeware.get("thermostat_bathroom", "thermostatHumidityAmbient")
    if waiting_for_shower:
      if homeware.get("thermostat_bathroom", "thermostatHumidityAmbient") > (initial_bathroom_humidity + BATHROOM_HUMIDITY_DELTA):
        shower_initiated = True

  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/occupancy":
    if payload == "OCCUPIED":
      if homeware.get("scene_ducha", "enable"):
        if shower_initiated:
          homeware.execute("scene_ducha", "enable", False)
          waiting_for_shower = False
          shower_initiated = False
          alert.voice("Veo que ya te has duchado. Dejo de priorizar el baño.")

# Set the power alert scene
def powerAlert(homeware, alert, topic, payload):
  if topic == "device/control":
    if payload["id"] == "current001" and payload["param"] == "brightness":
      global last_power_check
      global power_alert_counter
      power = payload["value"]
      if time.time() - last_power_check > DELAY_BETWEEN_POWER_ALERTS:
        last_power_check = time.time()
        # Power alerts
        if power >= 100:
          power_alert_counter += 1
          if power_alert_counter > 1:
            # Send voice and text alerts
            alert.voice("Sobrecarga de potencia, nivel crítico.")
            alert.message("Sobrecarga de potencia")
            # Change the status of some lights
            currentToggleSettings = {
              "emergencia": True
            }
            devices_id = ["rgb001", "rgb002", "rgb003"]
            for device_id in devices_id:
              homeware.execute(device_id, "currentToggleSettings", currentToggleSettings)
      if power < 85:
        if power_alert_counter > 1:
          power_alert_counter = 0
          # Send voice alerts
          alert.voice("Sistemas de potencia bajo control.")
          currentToggleSettings = {
            "emergencia": False
          }
          devices_id = ["rgb001", "rgb002", "rgb003"]
          for device_id in devices_id:
            homeware.execute(device_id, "currentToggleSettings", currentToggleSettings)
        
        if power_alert_counter == 1:
          power_alert_counter = 0

# Set sensors scene
def sensors(homeware, alert, topic, payload):
  pass
  # if topic == "device/scene_sensors_enable/enable":
  #   if not payload:
  #     homeware.execute("rgb003", "on", False)
  #     homeware.execute("hue_6", "on", False)
  #     homeware.execute("hue_sensor_12", "on", False)

# Set dim scene
def astro_day(homeware, alert, topic, payload):
  if topic == "device/scene_astro_day/enable":
    if not payload:
      homeware.execute("scene_dim", "enable", True)

# Headphones related logic
def headphones(homeware, alert, topic, payload):
  if topic == "device/scene_headphones/enable":
    if not homeware.get("ac_001", "currentFanSpeedSetting") == "Media":
      if homeware.get("thermostat_livingroom", "thermostatMode") in ["cool", "fan-only"]:
        if homeware.get("thermostat_livingroom", "thermostatTemperatureAmbient") > homeware.get("thermostat_livingroom", "thermostatTemperatureSetpoint"):
          homeware.execute("ac_001", "currentFanSpeedSetting", "Alta" if payload else "Baja")
