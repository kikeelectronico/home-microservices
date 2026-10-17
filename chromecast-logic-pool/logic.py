import time



def playing_lights(homeware, is_playing, previous_status):
  if not is_playing:
    if homeware.get("hue_17", "on") and homeware.get("pressure001", "occupancy") == "OCCUPIED" and homeware.get("scene_dim", "enable"):
      previous_status.setdefault("hue_17", {})
      previous_status["hue_17"]["brightness"] = homeware.get("hue_17","brightness")
      homeware.execute("hue_17", "brightness", 20)
    time.sleep(0.5)
    homeware.execute("hue_1", "on", False)
    time.sleep(0.5)
    homeware.execute("hue_9", "on", False)
    homeware.execute("hue_10", "on", False)
    is_playing = True

  return is_playing


def not_playing_lights(homeware, is_playing, previous_status):
  if is_playing:
    if "hue_17" in previous_status:
      if homeware.get("hue_17","on"):
        homeware.execute("hue_17", "brightness", previous_status["hue_17"]["brightness"])
    is_playing = False

  return is_playing
