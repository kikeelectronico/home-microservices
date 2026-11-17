import time

from constants import TOPICS


class NotificationVoiceService:

  def __init__(self):
    self.homeware = None
    self.voice = None

  def initialize(self, homeware, voice):
    self.homeware = homeware
    self.voice = voice

  def send_wakeup_message(self):
    hour = int(time.strftime("%H"))
    if hour >= 22 or (hour >= 0 and hour < 7):
      message = "buenas noches. Ya estoy preparada."
    elif hour >= 7 and hour < 15:
      message = "buenos días. Ya estoy preparada."
    else:
      message = "buenas tardes. Ya estoy preparada."

    self.voice.getAndPlay(message)

  def _handle_message(self, topic, payload):
    if topic == TOPICS[0]:
      if self.homeware.get("scene_awake", "enable"):
        message = payload.decode("utf-8")
        self.voice.getAndPlay(message)
    elif topic == TOPICS[1]:
      message = payload.decode("utf-8")
      self.voice.getAndPlay(message)
