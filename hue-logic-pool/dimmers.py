def mirror_on_off(homeware, service, preloaded_data):
  state = service["button"]["last_event"]
  if state == "initial_press":
    preloaded_data["hue_sensor_2/on"] = not homeware.get("hue_sensor_2", "on")
  elif state == "short_release":
    homeware.execute("hue_sensor_2", "on", preloaded_data["hue_sensor_2/on"])
  elif state == "long_press":
    value = not homeware.get("switch_hood", "on")
    homeware.execute("switch_hood", "on", value)


def mirror_brightness_up(homeware, service, preloaded_data):
  state = service["button"]["last_event"]
  if state == "initial_press":
    preloaded_data["hue_2/brightness"] = homeware.get("hue_2", "brightness")
  elif state == "short_release":
    value = preloaded_data["hue_2/brightness"]
    if value < 90:
      value += 10
    else:
      value = 100
    homeware.execute("hue_2", "brightness", value)
    homeware.execute("hue_3", "brightness", value)
  elif state == "long_press":
    value = not homeware.get("scene_dim", "enable")
    homeware.execute("scene_dim", "enable", value)


def mirror_brightness_down(homeware, service, preloaded_data):
  state = service["button"]["last_event"]
  if state == "initial_press":
    preloaded_data["hue_2/brightness"] = homeware.get("hue_2", "brightness")
  elif state == "short_release":
    value = preloaded_data["hue_2/brightness"]
    if value > 10:
      value -= 10
    else:
      value = 0
    homeware.execute("hue_2", "brightness", value)
    homeware.execute("hue_3", "brightness", value)


def mirror_color_temperature(homeware, service, preloaded_data):
  state = service["button"]["last_event"]
  if state == "initial_press":
    preloaded_data["hue_2/color"] = homeware.get("hue_2", "color")["temperatureK"]
  elif state == "short_release":
    current_temperature = preloaded_data["hue_2/color"]
    temperature_loop = [2700, 5000]
    try:
      new_index = temperature_loop.index(current_temperature) + 1
      if new_index == len(temperature_loop):
        new_index = 0
    except ValueError:
      new_index = 0
    new_temperature = temperature_loop[new_index]
    homeware.execute("hue_2", "color", {"temperatureK": new_temperature})
    homeware.execute("hue_3", "color", {"temperatureK": new_temperature})
