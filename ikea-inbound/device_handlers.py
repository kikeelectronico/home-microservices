import time


OUTLET_CURRENT_THRESHOLD = 0.15
IDS_MAP = {
  "109bf470-f27b-4a3d-bfb7-6ac284bb4ed9_1": "thermostat_livingroom"
}


def outlet(homeware, data, tasks, voltages_map):
  attributes = data.get("attributes")
  if "isReachable" in data:
    homeware.execute(data["id"], "online", data["isReachable"])
  if "isOn" in attributes:
    homeware.execute(data["id"], "on", attributes["isOn"])
  if "currentVoltage" in attributes:
    voltages_map[data["id"]] = attributes["currentVoltage"]
    homeware.execute(data["id"], "voltage", round(attributes["currentVoltage"], 1))
  if "currentAmps" in attributes:
    homeware.execute(data["id"], "current", round(attributes["currentAmps"], 1))
    if voltages_map.get(data["id"]):
      active_power = round(attributes["currentAmps"] * voltages_map.get(data["id"]))
      homeware.execute(data["id"], "power", active_power)
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


def motion_sensor(homeware, data):
  attributes = data.get("attributes")
  if "isReachable" in data:
    homeware.execute(data["id"], "online", data["isReachable"])
  if "batteryPercentage" in attributes:
    battery_level = attributes["batteryPercentage"]
    if battery_level == 100:
      descriptive_capacity_remaining = "FULL"
    elif battery_level >= 70:
      descriptive_capacity_remaining = "HIGH"
    elif battery_level >= 40:
      descriptive_capacity_remaining = "MEDIUM"
    elif battery_level >= 10:
      descriptive_capacity_remaining = "LOW"
    else:
      descriptive_capacity_remaining = "CRITICALLY_LOW"
    homeware.execute(data["id"], "descriptiveCapacityRemaining", descriptive_capacity_remaining)
    homeware.execute(
      data["id"],
      "capacityRemaining",
      [{"rawValue": battery_level, "unit": "PERCENTAGE"}]
    )
  if "isDetected" in attributes:
    homeware.execute(data["id"], "occupancy", "OCCUPIED" if attributes["isDetected"] else "UNOCCUPIED")


def air_purifier(homeware, data):
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
            case value if value < 25:
              sensor["currentSensorState"] = "new"
            case value if value < 90:
              sensor["currentSensorState"] = "good"
            case value if value < 100:
              sensor["currentSensorState"] = "replace soon"
            case value if value >= 100:
              sensor["currentSensorState"] = "replace now"
            case _:
              sensor["currentSensorState"] = "unknown"
          updated = True
        break
    if updated:
      homeware.execute(data["id"], "currentSensorStateData", homeware_current_sensors_state_data)
  if "fanMode" in attributes:
    ikea_fan_mode = attributes.get("fanMode", None)
    homeware_current_mode_settings = homeware.get(data["id"], "currentModeSettings")["Modo"]
    if "Modo" in homeware_current_mode_settings:
      homeware_mode = homeware_current_mode_settings["Modo"]
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
            motor_state = attributes["motorState"]
            if motor_state == 10 or motor_state == 20:
              new_homeware_fan_speed = "Baja"
            elif motor_state == 30:
              new_homeware_fan_speed = "Media"
            elif motor_state == 40 or motor_state == 50:
              new_homeware_fan_speed = "Alta"
            homeware_fan_speed = homeware.get(data["id"], "currentFanSpeedSetting")
            if new_homeware_fan_speed != homeware_fan_speed:
              homeware.execute(data["id"], "currentFanSpeedSetting", new_homeware_fan_speed)


def environment_sensor(homeware, data):
  attributes = data.get("attributes")
  if data["id"] not in IDS_MAP:
    return
  homeware_id = IDS_MAP[data["id"]]
  if "isReachable" in data:
    homeware.execute(homeware_id, "online", data["isReachable"])
  if "isOn" in attributes:
    homeware.execute(homeware_id, "online", attributes["isOn"])
  if "currentTemperature" in attributes:
    thermostat_temperature_ambient = round(attributes["currentTemperature"], 1)
    homeware.execute(homeware_id, "thermostatTemperatureAmbient", thermostat_temperature_ambient)
  if "currentRH" in attributes:
    thermostat_humidity_ambient = round(attributes["currentRH"], 0)
    homeware.execute(homeware_id, "thermostatHumidityAmbient", thermostat_humidity_ambient)
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


def water_leak_sensor(homeware, data):
  attributes = data.get("attributes")
  if "isReachable" in data:
    homeware.execute(data["id"], "online", data["isReachable"])
  if "batteryPercentage" in attributes:
    battery_level = attributes["batteryPercentage"]
    if battery_level == 100:
      descriptive_capacity_remaining = "FULL"
    elif battery_level >= 70:
      descriptive_capacity_remaining = "HIGH"
    elif battery_level >= 40:
      descriptive_capacity_remaining = "MEDIUM"
    elif battery_level >= 10:
      descriptive_capacity_remaining = "LOW"
    else:
      descriptive_capacity_remaining = "CRITICALLY_LOW"
    homeware.execute(data["id"], "descriptiveCapacityRemaining", descriptive_capacity_remaining)
    homeware.execute(
      data["id"],
      "capacityRemaining",
      [{"rawValue": battery_level, "unit": "PERCENTAGE"}]
    )
  if "waterLeakDetected" in attributes:
    homeware_current_sensors_state_data = homeware.get(data["id"], "currentSensorStateData")
    updated = False
    for sensor in homeware_current_sensors_state_data:
      if sensor.get("name") == "WaterLeak":
        new_sensor_state = "leak" if attributes.get("waterLeakDetected") else "no leak"
        if sensor.get("currentSensorState") != new_sensor_state:
          sensor["currentSensorState"] = new_sensor_state
          updated = True
        break
    if updated:
      homeware.execute(data["id"], "currentSensorStateData", homeware_current_sensors_state_data)
