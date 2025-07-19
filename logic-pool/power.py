import time

LIVINGROOM_POWER = 1645
BEDROOM_POWER = 1000
BATHROOM_POWER = 800
HEATER_POWER = 2200
MAX_POWER = 3500
TIME_TO_DISABLE_POWER_ALERT = 30
TIME_TO_ENABLE_POWER_ALERT = 10

power_timestamp = 0
power_pre_alert = False
power_alert = False
shower_state = 0

# Decide if a radiator should be turn on or off
def shouldHeat(homeware, thermostat_id, radiator_id, sensor_id = None, rule_14=False):
  state = homeware.get(thermostat_id, "all")
  sensor_open = homeware.get(sensor_id, "openPercent") == 100 if not sensor_id is None else False
  if (state["thermostatMode"] == "heat" and not sensor_open) or rule_14:
    ambient = state["thermostatTemperatureAmbient"]
    set_point = state["thermostatTemperatureSetpoint"] if not rule_14 else 14
    if ambient < set_point:
      return True
    elif ambient > set_point:
      return False
    else:
      return homeware.get(radiator_id,"on")
  else:
    return False
  
# Decide if a ac should be turn on or off
def shouldCool(homeware, thermostat_id, ac_id):
  state = homeware.get(thermostat_id, "all")
  if state["thermostatMode"] == "cool":
    ambient = state["thermostatTemperatureAmbient"]
    set_point = state["thermostatTemperatureSetpoint"]
    if ambient > (set_point + 0.2):
      return True
    elif ambient < set_point:
      return False
    else:
      return homeware.get(ac_id,"on")
  else:
    return False

# Control the power distribution
def powerManagment(homeware, topic, payload): 
  global power_timestamp
  global power_pre_alert
  global power_alert
  global shower_state

  TOPICS = [
    "device/scene_ducha/enable",
    "device/current001/brightness",
    "device/thermostat_livingroom",
    "device/thermostat_bathroom",
    "device/thermostat_dormitorio",
    "device/switch_at_home/on"
    "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent",
  ]

  if topic in TOPICS:
    # Verify power consumption and generate both pre alert and alert
    power = homeware.get("current001", "brightness")
    if power >= 100:
      if power_pre_alert:
        if (time.time() - power_timestamp) > TIME_TO_ENABLE_POWER_ALERT:
          power_alert = True
      else:
        power_pre_alert = True
        power_timestamp = time.time()
    # Diable pre alert
    if power_pre_alert and power < 100:
      power_pre_alert = False
    # Disable alert
    if power < 65 and power_alert and (time.time() - power_timestamp) > TIME_TO_DISABLE_POWER_ALERT:
      power_alert = False
      power_pre_alert = False
    # Power distribution
    if not power_alert:
      if homeware.get("scene_ducha", "enable"):
        # Shower state machine
        if shower_state in [0,1,2]: # Heat up water
          livingroom_radiator = False
          bedroom_radiator = False
          bathroom_radiator = False
          water_heater = True
          livingroom_ac = shouldCool(homeware, "thermostat_livingroom", "ac_001") or homeware.get("thermostat_livingroom", "thermostatMode") == "fan-only"
          shower_state = 1
          # Give the water heater time to start and the system to detect it
          if shower_state == 1:
            time.sleep(2)
            shower_state = 2
          elif shower_state == 2:
            if not homeware.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "isRunning"):
              shower_state == 3
        elif shower_state == 3: # If winter: heat up the bathroom air and keep the livingroom and water tank at temperature
          bathroom_radiator = shouldHeat(homeware, "thermostat_bathroom", "hue_12")
          # -
          livingroom_radiator = shouldHeat(homeware, "thermostat_livingroom", "hue_8", "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4") and (not homeware.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "isRunning")) and (not bathroom_radiator)
          bedroom_radiator = shouldHeat(homeware, "thermostat_dormitorio", "radiator002", "e6c2e2bd-5057-49bc-821f-a4b10e415ac6", rule_14)
          # -
          livingroom_ac = shouldCool(homeware, "thermostat_livingroom", "ac_001") or homeware.get("thermostat_livingroom", "thermostatMode") == "fan-only"
          water_heater = True
      else:
        shower_state = 0
        rule_14 = not homeware.get("switch_at_home", "on")
        livingroom_radiator = shouldHeat(homeware, "thermostat_livingroom", "hue_8", "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", rule_14)
        bedroom_radiator = shouldHeat(homeware, "thermostat_dormitorio", "radiator002", "e6c2e2bd-5057-49bc-821f-a4b10e415ac6", rule_14)
        bathroom_radiator = False
        livingroom_ac = shouldCool(homeware, "thermostat_livingroom", "ac_001") or homeware.get("thermostat_livingroom", "thermostatMode") == "fan-only"
        water_heater = not livingroom_radiator
    else:
      livingroom_radiator = False
      bedroom_radiator = False
      bathroom_radiator = False
      livingroom_ac = False
      water_heater = False

    # If the dishwasher is running
    if homeware.get("fc553d8b-1f45-4337-84ab-5c80a84e61ff_1", "isRunning"):
      water_heater = False
      bedroom_radiator = bedroom_radiator and (not livingroom_radiator)

    # Send new values to Homeware
    if homeware.get("scene_winter", "enable"):
      homeware.execute("hue_8","on",livingroom_radiator)
    homeware.execute("radiator002","on",bedroom_radiator)
    homeware.execute("hue_12","on",bathroom_radiator)
    homeware.execute("ac_001","on",livingroom_ac)

    # Check power budget
    if water_heater and (not homeware.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on")) and (homeware.get("current001", "brightness") > 40):
      water_heater = False

    homeware.execute("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1","on",water_heater)


