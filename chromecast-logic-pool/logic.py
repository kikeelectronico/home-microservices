import time

prev_player_playing_state = False 
prev_status = {}

def playingLights(homeware):
  global prev_player_playing_state
  if not prev_player_playing_state:
    if homeware.get("hue_4", "on"):
      prev_status.setdefault("hue_4", {})
      prev_status.setdefault("hue_5", {})
      prev_status["hue_4"]["brightness"] = homeware.get("hue_4","brightness")
      prev_status["hue_5"]["brightness"] = homeware.get("hue_5","brightness")
      homeware.execute("hue_4", "brightness", 20)
      homeware.execute("hue_5", "brightness", 20)
    time.sleep(0.5)
    homeware.execute("hue_1", "on", False)
    time.sleep(0.5)
    homeware.execute("hue_9", "on", False)
    homeware.execute("hue_10", "on", False)
    prev_status.setdefault("thermostat_livingroom", {})
    prev_status["thermostat_livingroom"]["thermostatMode"] = homeware.get("thermostat_livingroom", "thermostatMode")
    if prev_status["thermostat_livingroom"]["thermostatMode"] == "cool" and (not homeware.get("scene_headphones", "enable")):
      homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    prev_player_playing_state = True
      
def notPlayingLights(homeware):
  global prev_player_playing_state
  if prev_player_playing_state:
    if homeware.get("hue_4","on"):
      homeware.execute("hue_4", "brightness", prev_status["hue_4"]["brightness"])
      homeware.execute("hue_5", "brightness", prev_status["hue_5"]["brightness"])
    if prev_status["thermostat_livingroom"]["thermostatMode"] == "cool":
      homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    prev_player_playing_state = False
