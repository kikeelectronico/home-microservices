
def livingroom(homeware, topic, payload):
  if topic == "device/c8bd20a2-69a5-4946-b6d6-3423b560ffa9/brightness":
    if not homeware.get("scene_dim", "enable"):
      if int(payload) > 20:
        homeware.execute("scene_dim", "eneable", False)
        brightness = int((int(payload) * 1.4) + 16)
        homeware.execute("hue_6", "brightness", brightness)
        homeware.execute("hue_7", "brightness", brightness)
      else:
        homeware.execute("scene_dim", "eneable", True)