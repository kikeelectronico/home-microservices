import logging
import os
import requests
import time

RELOAD_TIME = 60


class Weather:
  __api_key = ""
  _weather = {}
  _last_update = 0
  _query = ""
  _fail_to_update = True

  def __init__(self):
    if os.environ.get("WHEATHER_API_KEY", "no") == "no":
      from dotenv import load_dotenv
      load_dotenv(dotenv_path="../.env")
    self.__api_key = os.environ.get("WHEATHER_API_KEY", "no_set")
    if self.__api_key == "no_set":
      logging.error("WHEATHER_API_KEY no set")
    self._query = os.environ.get("WHEATHER_QUERY", "no_set")
    if self._query == "no_set":
      logging.error("WHEATHER_QUERY no set")

  def updateWeather(self):
    if self.__api_key == "no_set" or self._query == "no_set":
      self._fail_to_update = True
      logging.error("Weather env vars aren't set")
      return None

    try:
      url = (
        "https://api.weatherapi.com/v1/forecast.json?key="
        + self.__api_key
        + "&q="
        + self._query
        + "&days=2&aqi=yes"
      )
      response = requests.request("GET", url, timeout=5)
      if response.status_code == 200:
        self._weather = response.json()
        self._fail_to_update = False
      else:
        logging.warning("Fail to update weather data. Status code: %s", response.status_code)
        self._fail_to_update = True
        return None
    except (requests.ConnectionError, requests.Timeout):
      logging.warning("Fail to update weather data. Connection error.")
      self._fail_to_update = True
      return None

    if "current" not in self._weather or "forecast" not in self._weather:
      return None

    return {
      "current": self._weather["current"],
      "forecast": self._weather["forecast"],
    }

  def getWeather(self):
    now = time.time()
    if now - self._last_update > RELOAD_TIME:
      self._last_update = now
      return self.updateWeather()

    if "current" not in self._weather or "forecast" not in self._weather:
      return None

    return {
      "current": self._weather["current"],
      "forecast": self._weather["forecast"],
    }
