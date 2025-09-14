import os
import requests
import time
import logging

RELOAD_TIME = 60

class Weather:

  __api_key = ""
  _weather = {}
  _last_update = 0
  _query = ""
  _alert_areas = ""
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
    self._alert_areas = os.environ.get("WHEATHER_ALERT_AREAS", "no_set")
    if self._alert_areas == "no_set": 
      logging.error("WHEATHER_ALERT_AREAS no set")
    self._alert_areas = self._alert_areas.split(",")

  def updateWeather(self):
    if self.__api_key == "no_set" or self._query == "no_set":
      self._fail_to_update = True
      logging.error("Wheather env vars aren't set")
    else:
      try:
        url = "https://api.weatherapi.com/v1/forecast.json?key=" + self.__api_key + "&q=" + self._query + "&days=2&aqi=yes&alerts=yes"
        response = requests.request("GET", url, timeout=5)
        if response.status_code == 200:
          self._weather = response.json()
          # Delete repeated alerts
          unique_alerts = []
          for _alert in self._weather["alerts"]["alert"]:
            alert = _alert
            del alert["effective"]
            del alert["expires"]
            if not alert in unique_alerts and alert["areas"] in self._alert_areas:
              unique_alerts.append(alert)
          self._weather["alerts"]["alert"] = unique_alerts

          self._fail_to_update = False
        else:
          logging.warning("Fail to update weather data. Status code: " + str(response.status_code))
          self._fail_to_update = True
      except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to update weather data. Conection error.")
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