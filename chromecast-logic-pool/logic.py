import time
import json

prev_player_playing_state = False 
prev_status = {}

def playingLights(homeware, mqtt_client):
  global prev_player_playing_state
  if not prev_player_playing_state:
    if homeware.get("hue_5", "on") and homeware.get("pressure001", "occupancy") == "OCCUPIED" and homeware.get("scene_dim", "enable"):
      prev_status.setdefault("hue_5", {})
      prev_status["hue_5"]["brightness"] = homeware.get("hue_5","brightness")
      homeware.execute("hue_5", "brightness", 20)
    time.sleep(0.5)
    homeware.execute("hue_1", "on", False)
    time.sleep(0.5)
    homeware.execute("hue_9", "on", False)
    homeware.execute("hue_10", "on", False)
    prev_player_playing_state = True
      
def notPlayingLights(homeware, mqtt_client):
  global prev_player_playing_state
  if prev_player_playing_state:
    if homeware.get("hue_5","on"):
      homeware.execute("hue_5", "brightness", prev_status["hue_5"]["brightness"])
    prev_player_playing_state = False
