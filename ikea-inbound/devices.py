import time

OUTLET_CURRENT_THRESHOLD = 0.2
IDS_MAP = {
  "109bf470-f27b-4a3d-bfb7-6ac284bb4ed9_1": "thermostat_livingroom"
}

def outlet(data, homeware, tasks, voltages_map):
  attributes = data.get("attributes")
  if "isReachable" in data:
    homeware.execute(data["id"], "online", data["isReachable"])
  if "isOn" in attributes:
    homeware.execute(data["id"], "on", attributes["isOn"])
  if "currentVoltage" in attributes:
    voltages_map[data["id"]] = attributes["currentVoltage"]
    homeware.publish(data["id"], "voltage", round(attributes["currentVoltage"],1))
  if "currentAmps" in attributes:
    homeware.publish(data["id"], "current", round(attributes["currentAmps"],1))
    if voltages_map.get(data["id"]):
      active_power = round(attributes["currentAmps"] * voltages_map.get(data["id"]))
      homeware.publish(data["id"], "power", active_power)
    if attributes["currentAmps"] > OUTLET_CURRENT_THRESHOLD:
      homeware.execute(data["id"], "isRunning", True)
      task_id = str(data["id"]) + "-" + "isRunning"
      if task_id in tasks:
        del tasks[task_id]
    else:
      task_id = str(data["id"]) + "-" + "isRunning"
      tasks[task_id] = {
        "time": time.time(),
        "device_id": str(data["id"]),
        "param": "isRunning",
        "value": False
      }

def motionSensor(data, homeware):
  attributes = data.get("attributes")
  if "isReachable" in data:
    homeware.execute(data["id"], "online", data["isReachable"])
  if "batteryPercentage" in data:
    battery_level = data["batteryPercentage"]
    if battery_level == 100: descriptiveCapacityRemaining = "FULL"
    elif battery_level >= 70: descriptiveCapacityRemaining = "HIGH"
    elif battery_level >= 40: descriptiveCapacityRemaining = "MEDIUM"
    elif battery_level >= 10: descriptiveCapacityRemaining ="LOW"
    else: descriptiveCapacityRemaining = "CRITICALLY_LOW"
    homeware.execute(data["id"],"descriptiveCapacityRemaining", descriptiveCapacityRemaining)
    homeware.execute(data["id"], "capacityRemaining", [{"rawValue": battery_level, "unit":"PERCENTAGE"}])
  if "isDetected" in attributes:
    homeware.execute(data["id"], "occupancy", "OCCUPIED" if attributes["isDetected"] else "UNOCCUPIED")

def airPurifier(data, homeware):
  attributes = data.get("attributes")
  if "isReachable" in data:
    if homeware.get(data["id"], "online") != data["isReachable"]:
      homeware.execute(data["id"], "online", data["isReachable"])
  if "currentPM25" in attributes:
    homeware_current_sensors_state_data = homeware.get(data["id"], "currentSensorStateData")
    updated = False
    for sensor in homeware_current_sensors_state_data:
      if sensor.get("name") == "PM2.5":
        new_raw_value = attributes.get("currentPM25")
        if sensor.get("rawValue") != new_raw_value:
          sensor["rawValue"] = new_raw_value
          updated = True
        break
    if updated:
      homeware.execute(data["id"], "currentSensorStateData", homeware_current_sensors_state_data)
  if "FilterLifeTime" in attributes:
    homeware_current_sensors_state_data = homeware.get(data["id"], "currentSensorStateData")
    updated = False
    for sensor in homeware_current_sensors_state_data:
      if sensor.get("name") == "FilterLifeTime":
        lifetime = attributes.get("FilterLifeTime")
        elapsed = attributes.get("filterElapsedTime")
        if lifetime and lifetime > 0:
            new_raw_value = round((elapsed / lifetime) * 100)
        else:
            new_raw_value = 0 

        if sensor.get("rawValue") != new_raw_value:
          sensor["rawValue"] = new_raw_value
          match new_raw_value:
            case p if p < 25:
                sensor["currentSensorState"] = "new"
            case p if p < 90:
                sensor["currentSensorState"] = "good"
            case p if p < 100:
                sensor["currentSensorState"] = "replace soon"
            case p if p >= 100:
                sensor["currentSensorState"] = "replace now"
            case _:
                sensor["currentSensorState"] = "unknown"
          updated = True
        break
    if updated:
      homeware.execute(data["id"], "currentSensorStateData", homeware_current_sensors_state_data)
  if "fanMode" in attributes:
    ikea_fan_mode = attributes.get("fanMode", None)
    homeware_mode = homeware.get(data["id"], "currentModeSettings")["Modo"]
    match ikea_fan_mode:
      case "off":
        if homeware_mode != "Apagado":
          homeware.execute(data["id"], "currentModeSettings", {"Modo": "Apagado"})
      case "auto":
        if homeware_mode != "Automático":
          homeware.execute(data["id"], "currentModeSettings", {"Modo": "Automático"})
      case "on":
        if homeware_mode != "Manual":
          homeware.execute(data["id"], "currentModeSettings", {"Modo": "Manual"})
      case "low" | "medium" | "high":
        if "motorState" in attributes:
          new_homeware_fan_speed = "Baja"
          motorState = attributes["motorState"]
          if motorState == 10 or motorState == 20: new_homeware_fan_speed = "Baja"
          elif motorState == 30: new_homeware_fan_speed = "Media"
          elif motorState == 40 or motorState == 50: new_homeware_fan_speed = "Alta"
          homeware_fan_speed = homeware.get(data["id"], "currentFanSpeedSetting")
          if new_homeware_fan_speed != homeware_fan_speed:
            homeware.execute(data["id"], "currentFanSpeedSetting", new_homeware_fan_speed)

def environmentSensor(data, homeware):
  attributes = data.get("attributes")
  homeware_id = IDS_MAP[data["id"]]
  if "isOn" in attributes:
    homeware.execute(homeware_id, "online", attributes["isOn"])
  if "currentTemperature" in attributes:
    thermostatTemperatureAmbient = round(attributes["currentTemperature"], 1)
    homeware.execute(homeware_id, "thermostatTemperatureAmbient", thermostatTemperatureAmbient)
  if "currentRH" in attributes:
    thermostatHumidityAmbient = round(attributes["currentRH"], 0)
    homeware.execute(homeware_id, "thermostatHumidityAmbient", thermostatHumidityAmbient)
  if "currentCO2" in attributes:
    homeware_current_sensors_state_data = homeware.get(homeware_id, "currentSensorStateData")
    updated = False
    for sensor in homeware_current_sensors_state_data:
      if sensor.get("name") == "CarbonDioxideLevel":
        new_raw_value = attributes.get("currentCO2")
        if sensor.get("rawValue") != new_raw_value:
          sensor["rawValue"] = new_raw_value
          updated = True
        break
    if updated:
      homeware.execute(homeware_id, "currentSensorStateData", homeware_current_sensors_state_data)
  if "currentPM25" in attributes:
    homeware_current_sensors_state_data = homeware.get(homeware_id, "currentSensorStateData")
    updated = False
    for sensor in homeware_current_sensors_state_data:
      if sensor.get("name") == "PM2.5":
        new_raw_value = attributes.get("currentPM25")
        if sensor.get("rawValue") != new_raw_value:
          sensor["rawValue"] = new_raw_value
          updated = True
        break
    if updated:
      homeware.execute(homeware_id, "currentSensorStateData", homeware_current_sensors_state_data)
