from google.cloud import texttospeech
import threading
import os
import json

DEVICES_IPS = {
  "livingroom": "192.168.10.15",
  "bedroom": "192.168.10.16",
  "bathroom": "192.168.10.17"
}

class Voice:

  speakers = ""

  def __init__(self, homeware):
    self.text_to_speech_client = texttospeech.TextToSpeechClient()
    self.voice = texttospeech.VoiceSelectionParams(
      language_code="es-ES",
      name="es-ES-Chirp3-HD-Kore"
    )
    self.audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    self.homeware = homeware

  # Genereate mp3 file if needed
  def getFile(self, text):
    # Create file name
    file_name = text
    for c in ((" ", ""),("ó","o"),(".", ""),("á", "a"),("é", "e"),("í", "i"),("ú", "u"),("!", ""),("¡", ""),("?", ""),("¿", "")):
      file_name = file_name.replace(*c)
    file_path = "audio/" + file_name+".mp3"
    # If the mp3 file doesn't exists
    if not os.path.exists(file_path):
      # Get the speech binary from Google TTS
      synthesis_input = texttospeech.SynthesisInput(text=text)
      response = self.text_to_speech_client.synthesize_speech(
        input=synthesis_input, voice=self.voice, audio_config=self.audio_config
      )
      # Create the mp3 file
      with open(file_path, "wb") as out:
        out.write(response.audio_content)
    return file_path

  # Stream the mp3 to the smart speakers
  def playFile(self, file_path):
    class runCommandThread(threading.Thread):
      def __init__(self, command):
        threading.Thread.__init__(self)
        self.cmd = command

      def run(self):
        os.system(self.cmd)

    threads = []
    if self.speakers == "all":
      for device in DEVICES_IPS:
        threads.append(runCommandThread("catt -d " + DEVICES_IPS[device] + " cast " + file_path))
        threads[-1].start()
    else:
      device = self.getRoom()
      threads.append(runCommandThread("catt -d " + DEVICES_IPS[device] + " cast " + file_path))
      threads[-1].start()

  def setSpeakers(self, speakers):
    self.speakers = speakers
    
  def getRoom(self):
    if self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "currentToggleSettings")["last_seen"]:
      return "livingroom"
    if self.homeware.get("c2b38173-883e-4766-bcb5-0cce2dc0e00e", "currentToggleSettings")["last_seen"]:
      return "bedroom"
    if self.homeware.get("06612edc-4b7c-4ef3-9f3c-157b9d482f8c", "currentToggleSettings")["last_seen"]:
      return "bathroom"

  # Play an announcement
  def getAndPlay(self, text):
    file_path = self.getFile(text)
    self.playFile(file_path)
    self.speakers = ""