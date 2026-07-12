MIN_LIVINGROOM_DARKNESS_TRIGGER = 15

def sofaLight(homeware, topic, payload):
  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness" or topic == "device/pressure001/occupancy":
    if payload == "OCCUPIED":
      homeware.execute("hue_1", "on", False)
    else:
      light_level = int(payload) if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness" else homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness")
      occupancy = payload if topic == "device/pressure001/occupancy" else homeware.get("pressure001", "occupancy")
      if light_level < MIN_LIVINGROOM_DARKNESS_TRIGGER and homeware.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
        homeware.execute("hue_1", "on", True)
      elif light_level >= MIN_LIVINGROOM_DARKNESS_TRIGGER and homeware.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
        homeware.execute("hue_1", "on", False)

def workbenchLight(homeware, topic, payload):  
  if topic == "device/temp_switch/on":
    if payload:
      homeware.execute("hue_4", "color", {"temperatureK": 5000})
      homeware.execute("hue_5", "color", {"temperatureK": 5000})
      homeware.execute("hue_4", "brightness", 100)
      homeware.execute("hue_5", "brightness", 100)
      homeware.execute("hue_4", "on", True)
      homeware.execute("hue_5", "on", True)
    else:
      homeware.execute("hue_4", "on", False)
      homeware.execute("hue_5", "on", False)

WORKTABLE_DYNAMIC_BRIGNTNESS_MULTIPLIER = 1.5

def worktableLight(homeware, topic, payload):
  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness":
    if homeware.get("scene_awake", "enable"):
      light_level = int(payload)
      if light_level < MIN_LIVINGROOM_DARKNESS_TRIGGER:
        homeware.execute("hue_9", "brightness", 10)
        homeware.execute("hue_10", "brightness", 10)
      else:
        brightness = int(light_level*WORKTABLE_DYNAMIC_BRIGNTNESS_MULTIPLIER)
        homeware.execute("hue_9", "brightness", brightness)
        homeware.execute("hue_10", "brightness", brightness)

  if topic == "device/0b97c3c8-cb02-4f6d-9e60-d5755b25b968_1/occupancy":
    if payload == "OCCUPIED" and homeware.get("pressure001", "occupancy") == "UNOCCUPIED":
      homeware.execute("hue_9", "on", True)
      homeware.execute("hue_10", "on", True)