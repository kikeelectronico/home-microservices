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

  def __init__(self, logger):
    if os.environ.get("WHEATHER_API_KEY", "no") == "no":
      from dotenv import load_dotenv
      load_dotenv(dotenv_path="../.env")
    self.__api_key = os.environ.get("WHEATHER_API_KEY", "no_set")
    if self.__api_key == "no_set": 
      logger.log("WHEATHER_API_KEY no set", severity="ERROR")
    self._query = os.environ.get("WHEATHER_QUERY", "no_set")
    if self._query == "no_set": 
      logger.log("WHEATHER_QUERY no set", severity="ERROR")
    self.logger = logger

  def updateWeather(self):
    if self.__api_key == "no_set" or self._query == "no_set":
      self._fail_to_update = True
      self.logger.log("Wheather env vars aren't set", severity="ERROR")
    else:
      try:
        url = "https://api.weatherapi.com/v1/forecast.json?key=" + self.__api_key + "&q=" + self._query + "&days=2&aqi=yes&alerts=yes"
        response = requests.request("GET", url, verify=False, timeout=5)
        if response.status_code == 200:
          self._weather = response.json()
          # Delete repeated alerts
          unique_alerts = []
          for alert in self._weather["alerts"]["alert"]:
            if not alert in unique_alerts:
              unique_alerts.append(alert)
          self._weather["alerts"]["alert"] = unique_alerts

          self._fail_to_update = False
        else:
          self.logger.log("Fail to update weather data. Status code: " + str(response.status_code), severity="WARNING")
          self._fail_to_update = True
      except (requests.ConnectionError, requests.Timeout) as exception:
        self.logger.log("Fail to update weather data. Conection error.", severity="WARNING")
        self._fail_to_update = False

  def getWeather(self):
    now = time.time()
    if now - self._last_update > RELOAD_TIME:
      self._last_update = now
      self.updateWeather()

    current_flag = "current" in self._weather.keys()
    forecast_flag = "forecast" in self._weather.keys()
    alerts_flag = "alerts" in self._weather.keys()

    return (self._fail_to_update, current_flag, self._weather["current"], forecast_flag, self._weather["forecast"], alerts_flag, self._weather["alerts"])