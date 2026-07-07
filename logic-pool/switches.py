
def bedroom(homeware, topic, payload):
  if topic == "device/hue_sensor_12/on":
    if payload:
      if homeware.get("scene_dim","enable"):
        homeware.execute("rgb003","on",True)
      else:
        homeware.execute("hue_6","on",True)
    else:
      homeware.execute("hue_6","on",False)
      homeware.execute("rgb003","on",False)