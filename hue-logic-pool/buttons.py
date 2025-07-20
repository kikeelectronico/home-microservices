buttons_preloaded_data = {}

def bedroom(service, homeware):
  if service["id"] == "a4ac42ce-414e-483b-b13c-0f2c5e7dc879":
    global buttons_preloaded_data
    state = service["button"]["last_event"]
    if state == "initial_press":
      buttons_preloaded_data["hue_sensor_12/on"] = not homeware.get("hue_sensor_12","on")
    elif state == "short_release":
      homeware.execute("hue_sensor_12","on", buttons_preloaded_data["hue_sensor_12/on"])
    elif state == "long_press":
      value = not homeware.get("scene_dim","enable")
      homeware.execute("scene_dim","enable",value)

def kitchen(service, homeware):
  if service["id"] == "3ea75bb9-6bf6-4a2e-8f85-f9013e6279bc":
    global buttons_preloaded_data
    state = service["button"]["last_event"]
    if state == "initial_press":
      buttons_preloaded_data["light004/on"] = not homeware.get("light004","on")
    elif state == "short_release":
      homeware.execute("light004","on",buttons_preloaded_data["light004/on"])
    elif state == "long_press":
      new_state = not homeware.get("hue_5","on")
      homeware.execute("hue_5", "on", new_state)

def bathroom(service, homeware):
  if service["id"] == "04db1f5f-3467-4a26-9e17-7d9e6586a536":
    global buttons_preloaded_data
    state = service["button"]["last_event"]
    if state == "initial_press":
      buttons_preloaded_data["hue_sensor_14/on"] = not homeware.get("hue_sensor_14","on")
    elif state == "short_release":
      homeware.execute("hue_sensor_14","on",buttons_preloaded_data["hue_sensor_14/on"])
    elif state == "long_press":
      value = not homeware.get("scene_dim","enable")
      homeware.execute("scene_dim","enable",value)
      
             