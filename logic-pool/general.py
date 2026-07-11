# Do several task when leaving and arriving at home
def atHome(homeware, topic, payload):
  if topic == "device/switch_at_home/on":
    if payload:
      if homeware.get("scene_winter", "enable"):
        homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21)
        homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
        homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
        homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
      homeware.execute("hue_17", "on", True)
      homeware.execute("hue_11", "on", True)
      homeware.execute("hue_15", "on", True)
      homeware.execute("rgb001", "on", True)
      homeware.execute("hue_16", "on", True)
      homeware.execute("switch_prepare_home", "on", False)
    else:
      homeware.execute("thermostat_dormitorio", "thermostatMode", "off")
      homeware.execute("thermostat_livingroom", "thermostatMode", "off")
      homeware.execute("thermostat_livingroom", "thermostat_bathroom", "off")
      homeware.execute("hue_sensor_14", "on", False)
      homeware.execute("hue_sensor_12", "on", False)
      homeware.execute("light004", "on", False)
      homeware.execute("light003", "on", False)
      homeware.execute("hue_9", "on", False)
      homeware.execute("hue_10", "on", False)
      homeware.execute("hue_11", "on", False)
      homeware.execute("hue_15", "on", False)
      homeware.execute("hue_17", "on", False)
      homeware.execute("rgb001", "on", False)
      homeware.execute("hue_16", "on", False)