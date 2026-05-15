def pyramids(homeware, topic, payload):
  if topic == "device/hue_17/brightness":
    homeware.execute("hue_17", "on", True)
