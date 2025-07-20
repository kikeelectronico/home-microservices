def pyramids(homeware, topic, payload):
  if topic == "device/hue_5/brightness":
    homeware.execute("hue_5", "on", True)

def workTable(homeware, topic, payload):
  if topic in ["device/hue_9/brightness", "device/hue_10/brightness"]:
    homeware.execute("hue_9", "on", True)
    homeware.execute("hue_10", "on", True)