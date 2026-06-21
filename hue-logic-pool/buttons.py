buttons_preloaded_data = {}

def bedroom(service, homeware):
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
  global buttons_preloaded_data
  state = service["button"]["last_event"]
  if state == "initial_press":
    buttons_preloaded_data["light004/on"] = not homeware.get("light004","on")
  elif state == "short_release":
    homeware.execute("light004","on",buttons_preloaded_data["light004/on"])
  elif state == "long_press":
    new_state = not homeware.get("hue_17","on")
    homeware.execute("hue_17", "on", new_state)

def bathroom(service, homeware):
  global buttons_preloaded_data
  state = service["button"]["last_event"]
  if state == "initial_press":
    buttons_preloaded_data["hue_sensor_14/on"] = not homeware.get("hue_sensor_14","on")
  elif state == "short_release":
    homeware.execute("hue_sensor_14","on",buttons_preloaded_data["hue_sensor_14/on"])
  elif state == "long_press":
    value = not homeware.get("hallway_switch","on")
    homeware.execute("hallway_switch","on",value)
      
             