import datetime
import logging
import math
import time

import requests

from constants import HEARTBEAT_TOPIC
from shutdown import stop_requested, wait_for_stop


class CircadianControllerService:

  def __init__(self):
    self.settings = None
    self.mqtt_client = None
    self.homeware = None
    self.last_heartbeat_timestamp = 0
    self.just_executed = False
    self.solar_cycle = {
      "sunset": 0,
      "sunrise": 0
    }

  def initialize(self, settings, mqtt_client, homeware):
    self.settings = settings
    self.mqtt_client = mqtt_client
    self.homeware = homeware

    today = datetime.datetime.now()
    hour = today.strftime("%H:%M:%S")
    logging.info("Hora local " + str(hour))
    self._update_solar_data()

  def _update_solar_data(self):
    try:
      url = "https://api.weatherapi.com/v1/astronomy.json?key=" + self.settings.wheather_api_key + "&q=" + self.settings.wheather_query
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
        data = response.json()
        sunset = data["astronomy"]["astro"]["sunset"].split(" ")[0]
        sunset = int(sunset.split(":")[0]) + 12 + (int(sunset.split(":")[1])/60)
        sunrise = data["astronomy"]["astro"]["sunrise"].split(" ")[0]
        sunrise = int(sunrise.split(":")[0]) + (int(sunrise.split(":")[1])/60)
        self.solar_cycle = {
          "sunrise": sunrise,
          "sunset": sunset
        }
      else:
        logging.warning("Fail to update weather data. Status code: " + str(response.status_code))
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to update weather data. Conection error.")

  def _color_temperature(self, hour, sunrise, sunset, Tmin=2200, Tmax=6500):
    h_mid = (sunrise + sunset) / 2
    day_length = sunset - sunrise
    if day_length <= 0:
      return Tmin

    if sunrise <= hour <= sunset:
      angle = math.pi * (hour - h_mid) / (day_length / 2)
      temp = Tmin + (Tmax - Tmin) * (0.5 * math.cos(angle) + 0.5)
      return int(temp)
    else:
      return Tmin

  def run(self):
    while not stop_requested():
      # Get current time
      today = datetime.datetime.now()
      hour = int(today.strftime("%H"))
      minute = int(today.strftime("%M"))

      # Update astrodata
      if hour == 4 and minute == 0 and not self.just_executed:
        self.just_executed = True
        self._update_solar_data()
      if hour == 4 and minute == 5 and self.just_executed:
        self.just_executed = False

      # Calculate color temperature and adjust lights
      if self.homeware.get("scene_circadian_controller_enable", "enable"):
        color_temperature = self._color_temperature((hour + (minute/60)), self.solar_cycle["sunrise"], self.solar_cycle["sunset"])
        self.homeware.execute("hue_1", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_4", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_5", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_6", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_9", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_10", "color", {"temperatureK": color_temperature})
        if not self.homeware.get("hue_15", "currentToggleSettings")["emergencia"]:
          self.homeware.execute("hue_15", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_16", "color", {"temperatureK": color_temperature})
        self.homeware.execute("hue_17", "color", {"temperatureK": color_temperature})

      # Send the heartbeat
      if time.time() - self.last_heartbeat_timestamp > 10:
        self.mqtt_client.publish(HEARTBEAT_TOPIC, self.settings.service_id)
        self.last_heartbeat_timestamp = time.time()

      wait_for_stop(55)
