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