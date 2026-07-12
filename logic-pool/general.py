# Do several task when leaving and arriving at home
def atHome(homeware, topic, payload):
  if topic == "device/switch_at_home/on":
    if payload:
      if homeware.get("scene_winter", "enable"):
        homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
        homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
      homeware.execute("switch_prepare_home", "on", False)
    else:
      homeware.execute("thermostat_livingroom", "thermostatMode", "off")
      homeware.execute("thermostat_livingroom", "thermostat_bathroom", "off")