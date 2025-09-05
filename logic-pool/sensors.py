
def livingroom(homeware, topic, payload):
  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness":
    if not homeware.get("scene_dim", "enable"):
      # if int(payload) > 20:
        # homeware.execute("scene_dim", "eneable", False)
      brightness = int((int(payload) * 1.4) + 20)
      if not homeware.get("hue_sensor_12", "on"):
        homeware.execute("hue_6", "brightness", brightness)
      homeware.execute("hue_7", "brightness", brightness)
      # else:
      #   homeware.execute("scene_dim", "eneable", True)

def sofa(homeware, topic, payload):
  if topic == "device/pressure001/occupancy":
    if payload == "OCCUPIED":
      homeware.execute("hue_9", "on", False)
      homeware.execute("hue_10", "on", False)

def bedroom(homeware, topic, payload):
  if topic == "device/pressure002/occupancy":
    if homeware.get("scene_astro_day","enable"):
      homeware.execute("scene_sensors_enable", "enable", payload == "UNOCCUPIED")
      if homeware.get("scene_dim", "enable"):
        homeware.execute("rgb003", "on", payload == "UNOCCUPIED")
      else:
          homeware.execute("rgb003", "on", payload == "OCCUPIED")
          homeware.execute("hue_6", "on", payload == "UNOCCUPIED")

def workTable(homeware, topic, payload):
  if topic == "device/0b97c3c8-cb02-4f6d-9e60-d5755b25b968_1/occupancy":
    if payload == "OCCUPIED" and homeware.get("pressure001", "occupancy" == "UNOCCUPIED"):
      homeware.execute("hue_9", "on", True)
      homeware.execute("hue_10", "on", True)