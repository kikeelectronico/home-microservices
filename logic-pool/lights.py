def pyramids(homeware, topic, payload):
  if topic == "device/hue_5/brightness":
    homeware.execute("hue_5", "on", True)
