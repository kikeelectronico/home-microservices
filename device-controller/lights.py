def resetEdisonBulb(homeware, topic, payload):
  if topic == "device/hue_11/color":
    if not payload["temperatureK"] == 2200:
        homeware.execute("hue_11","color", { "temperatureK": 2200 })

  if topic == "device/hue_11/brightness":
    if int(payload) > 35:
        homeware.execute("hue_11","brightness", 35)

MIN_LIVINGROOM_DARKNESS_TRIGGER = 20

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
  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness":
    if homeware.get("scene_awake", "enable") and not homeware.get("temp_switch", "on"):
      light_level = int(payload)
      if light_level < MIN_LIVINGROOM_DARKNESS_TRIGGER:
        homeware.execute("hue_4", "color", {"temperatureK": 2700})
        homeware.execute("hue_4", "brightness", 10)
        homeware.execute("hue_4", "on", True)
      else:
        homeware.execute("hue_4", "on", False)
  
  if topic == "device/temp_switch/on":
    if payload:
      homeware.execute("hue_4", "color", {"temperatureK": 5000})
      homeware.execute("hue_4", "brightness", 100)
    homeware.execute("hue_4", "on", payload)