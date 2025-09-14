import os
import requests
from io import BytesIO
import time
# from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import logging

class Spotify:

  __refresh_token = ""
  __app_auth = ""
  __access_token = ""
  _tries = 0
  _playing = {}
  _last_track = ""
  _track_image = ""
  _track_image_position = "0"
  _stop_until = 0
  _service_unavailable_counter = 0

  def __init__(self):
    if os.environ.get("SPOTIFY_REFRESH_TOKEN", "no") == "no":
      from dotenv import load_dotenv
      load_dotenv(dotenv_path="../.env")
    self.__refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN", "no_set")
    if self.__refresh_token == "no_set": 
      logging.error("SPOTIFY_REFRESH_TOKEN no set")
    self.__app_auth = os.environ.get("SPOTIFY_APP_AUTH", "no_set")
    if self.__app_auth == "no_set": 
      logging.error("SPOTIFY_APP_AUTH no set")
    self._covers_ddbb = os.environ.get("COVERS_DDBB", "no_set")
    if self._covers_ddbb == "no_set": 
      logging.error("COVERS_DDBB no set")
    # Initialize the keras model
    np.set_printoptions(suppress=True)
    # self._track_image_model = load_model("track_image_model/keras_model.h5", compile=False)
    # self._track_image_class_names = open("track_image_model/labels.txt", "r").readlines()
    # self._track_image_data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

  def updatePlaying(self, max_tries=2):
    if self.__refresh_token == "no_set" or self.__app_auth == "no_set" or self._covers_ddbb == "no_set":
      spotify = {
        "playing": False,
        "quota_exceeded": False
      }

      self._playing = spotify
      logging.warning("Spotify env vars aren't set", severity="ERROR")
    else:
      self._tries += 1
      if self.__access_token == "":
        self.updateAccessToken()
      try:
        # Plaiyng
        url = "https://api.spotify.com/v1/me/player/"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + self.__access_token
        }
        response = requests.request("GET", url, headers=headers, data=payload, timeout=5)

        if response.status_code == 200:
          self._service_unavailable_counter = 0
          playing = response.json()
          if playing['is_playing'] and not playing["item"] is None:
            if not self._last_track == playing['item']['id'] and time.time() > self._stop_until:
              # Track info
              url= "https://api.spotify.com/v1/tracks/" + playing['item']['id']
              payload={}
              headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.__access_token
              }
              response = requests.request("GET", url, headers=headers, data=payload, timeout=5)

              if response.status_code == 200:
                track = response.json()
                self._track_image = track['album']['images'][0]['url']
                self._last_track = playing['item']['id']

                self.analyzeTrackImage()

                spotify = {
                  "playing": playing['is_playing'],
                  "device": playing['device']['name'],
                  "volume": playing['device']['volume_percent'],
                  "track_name": playing['item']['name'],
                  "time": playing['progress_ms'],
                  "duration": playing['item']['duration_ms'],
                  "artists": ", ".join([artist["name"] for artist in playing['item']['artists']]),
                  "image": self._track_image,
                  "image_position": self._track_image_position,
                  "quota_exceeded": False
                }

                self._tries = 0
                self._playing = spotify

              elif response.status_code == 429:
                logging.warning("Spotify API quota exceeded")
                self._stop_until = time.time() + (int(response.headers['retry-after'])*1000)

                spotify = {
                  "playing": playing['is_playing'],
                  "device": playing['device']['name'],
                  "volume": playing['device']['volume_percent'],
                  "track_name": playing['item']['name'],
                  "time": playing['progress_ms'],
                  "duration": playing['item']['duration_ms'],
                  "artists": ", ".join([artist["name"] for artist in playing['item']['artists']]),
                  "image": "",
                  "image_position": self._track_image_position,
                  "quota_exceeded": True
                }

                self._playing = spotify
            
            else:
              spotify = {
                  "playing": playing['is_playing'],
                  "device": playing['device']['name'],
                  "volume": playing['device']['volume_percent'],
                  "track_name": playing['item']['name'],
                  "time": playing['progress_ms'],
                  "duration": playing['item']['duration_ms'],
                  "artists": ", ".join([artist["name"] for artist in playing['item']['artists']]),
                  "image": self._track_image,
                  "image_position": self._track_image_position,
                  "quota_exceeded": time.time() < self._stop_until
                }

              self._tries = 0
              self._playing = spotify

          else:
            spotify = {
              "playing": False,
              "quota_exceeded": False
            }

            self._tries = 0
            self._playing = spotify

        elif response.status_code == 204:
          logging.info("Spotify API returns a 204 code")
          spotify = {
            "playing": False,
            "quota_exceeded": False
          }

          self._playing = spotify

        elif response.status_code == 429:
          logging.warning("Spotify API quota exceeded")
          spotify = {
            "playing": False,
            "quota_exceeded": True
          }

          self._playing = spotify

        elif response.status_code == 503:
          logging.info("Spotify API returns a 503 code")
          if self._service_unavailable_counter == 0:
            self._service_unavailable_counter += 1
          else:
            spotify = {
              "playing": False,
              "quota_exceeded": False
            }

            self._playing = spotify

        else:
          error = response.json()['error']
          logging.info("Spotify API returns a " + str(error['status']) + " code")
          spotify = {
            "playing": False,
            "quota_exceeded": False
          }

          if error['status'] == 400 or error['status'] == 401:
            if self.updateAccessToken() and self._tries < max_tries:
              self._playing = self.getPlaying(max_tries)
            else:
              self._playing = spotify
          else:
            self._playing = spotify

      except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get Spotify player data. Conection error.")
        spotify = {
          "playing": False,
          "quota_exceeded": False
        }

  def updateAccessToken(self):
    try:
      logging.info("Updating Spotify access token")
      url = "https://accounts.spotify.com/api/token"
      payload='grant_type=refresh_token&refresh_token=' + self.__refresh_token
      headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic ' + self.__app_auth
      }

      response = requests.request("POST", url, headers=headers, data=payload, timeout=5)
      if response.status_code == 200:
        self.__access_token = response.json()['access_token']
        logging.info("Spotify access token updated")
        return True
      else:
        logging.warning("Fail to update Spotify access token. Status code: " + response.status_code)
        return False
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to update Spotify access token. Conection error.")
      return False

  def getPlaying(self, max_tries=2):
    self.updatePlaying(max_tries)

    return self._playing

  def analyzeTrackImage(self):
    try:
      response = requests.get(self._track_image)
      image = Image.open(BytesIO(response.content)).convert("RGB")

      if response.status_code == 200:
        try:
          pass
          # size = (224, 224)
          # image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
          # image_array = np.asarray(image)
          # normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
          # self._track_image_data[0] = normalized_image_array

          # prediction = self._track_image_model.predict(self._track_image_data)
          # index = np.argmax(prediction)
          # class_name = self._track_image_class_names[index]
          # self._track_image_position = class_name[2:-1]
        except:
          logging.warning("Fail to analyze a track image from Spotify")
      else:
        logging.warning("Fail to get a track image from Spotify. Error code: " + response.status_code)
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to get a track image from Spotify. Conection error.")