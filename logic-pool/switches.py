
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

def bathroom(homeware, topic, payload):
  if topic == "device/hue_sensor_14/on":
    if payload:
      if homeware.get("scene_dim","enable"):
        homeware.execute("hue_sensor_2","on",True)
      else:
        homeware.execute("light001","on",True)
    else:
      homeware.execute("hue_sensor_2","on",False)
      homeware.execute("light001","on",False)

def mirror(homeware, topic, payload):
  if topic == "device/hue_sensor_2/on":
    if payload:
      homeware.execute("hue_2","on",True)
      homeware.execute("hue_3","on",True)
    else:
      homeware.execute("hue_2","on",False)
      homeware.execute("hue_3","on",False)