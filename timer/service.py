import datetime
import logging
import time

import requests

from constants import HEARTBEAT_TOPIC
from shutdown import stop_requested, wait_for_stop


class TimerService:

  def __init__(self, settings, mqtt_client, homeware, alert):
    self.settings = settings
    self.mqtt_client = mqtt_client
    self.homeware = homeware
    self.alert = alert
    self.last_heartbeat_timestamp = 0
    self.just_executed = ""
    self.astro_data = {
      "sunset": 0,
      "sunrise": 0
    }

  def _update_astro_data(self):
    try:
      url = "https://api.weatherapi.com/v1/astronomy.json?key=" + self.settings.wheather_api_key + "&q=" + self.settings.wheather_query
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
        data = response.json()
        sunset = data["astronomy"]["astro"]["sunset"].split(" ")[0]
        sunset = str(int(sunset.split(":")[0]) + 12) + ":" + sunset.split(":")[1] + ":00"
        sunrise = data["astronomy"]["astro"]["sunrise"].split(" ")[0]
        sunrise = str(int(sunrise.split(":")[0])) + ":" + sunrise.split(":")[1] + ":00"
        self.astro_data = {
          "sunrise": sunrise,
          "sunset": sunset
        }
      else:
        logging.warning("Fail to update weather data. Status code: " + str(response.status_code))
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to update weather data. Conection error.")

  def run(self):
    today = datetime.datetime.now()
    hour = today.strftime("%H:%M:%S")
    logging.info("Hora local " + str(hour))
    self._update_astro_data()

    while not stop_requested():
      today = datetime.datetime.now()
      minute = today.strftime("%M")
      if minute == "05":
        self.homeware.execute("switch_hood", "on", True)
      elif minute == "15":
        self.homeware.execute("switch_hood", "on", False)

      hour = today.strftime("%H:%M:%S")
      self._run_time_blocks(today, hour)
      self._publish_heartbeat_if_due()
      wait_for_stop(0.1)

  def _run_time_blocks(self, today, hour):
    # Time blocks
    # if hour == "03:00:00" and not hour == self.just_executed:
    #   self.just_executed = hour
    #   self.homeware.execute("hue_8", "on", False)
    if hour == "04:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      self._update_astro_data()
      self.homeware.execute("scene_circadian_controller_enable", "enable", True)
    # elif hour == "06:00:00" and not hour == self.just_executed:
    #   self.just_executed = hour
    #   self.homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    # elif hour == "07:00:00" and not hour == self.just_executed:
    #   self.just_executed = hour
    #   self.homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    elif hour == "08:30:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("scene_winter", "enable"):
          self.homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21)
          self.homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          self.homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
          self.homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
          self.homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
    elif hour == "08:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("scene_summer", "enable"):
          self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 26.5)
          # self.homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    elif hour == "08:55:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        self.alert.voice("5 minutos para las nueve.")
    elif hour == "09:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("scene_winter", "enable"):
          self.homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 20)
          self.homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          self.homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
        # elif self.homeware.get("scene_summer", "enable"):
        #   self.homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    elif hour == "10:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if (weekday in [5,6] or self.homeware.get("scene_on_vacation", "enable")) and self.homeware.get("switch_at_home", "on"):
        if self.homeware.get("scene_winter", "enable"):
          self.homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21)
          self.homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          self.homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
          self.homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
          self.homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
    elif hour == "10:30:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness") < 20 and self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          self.alert.voice("Poca luz.")
    elif hour == "12:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      if self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("scene_dim", "enable") and self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          self.alert.voice("Luz indirecta activada.")
      weekday = today.weekday()
      if (weekday in [5,6] or self.homeware.get("scene_on_vacation", "enable")) and self.homeware.get("switch_at_home", "on"):
        if self.homeware.get("scene_winter", "enable"):
          self.homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 20)
          self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          self.homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
    elif hour == "16:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and self.homeware.get("switch_at_home", "on") and (not self.homeware.get("scene_on_vacation", "enable")):
        if self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness") < 20 and self.homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          self.alert.voice("Poca luz.")
    elif hour == "22:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      if self.homeware.get("scene_winter", "enable"):
        self.homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 19)
        self.homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
        self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 21)
        self.homeware.execute("thermostat_bathroom", "thermostatMode", "off")
      self.homeware.execute("scene_dim","enable",True)
    elif hour == "23:00:00" and not hour == self.just_executed:
      self.just_executed = hour
      if self.homeware.get("scene_winter", "enable"):
        self.homeware.execute("thermostat_livingroom", "thermostatMode", "off")

    # Astro time blocks
    if hour == "0" + self.astro_data["sunrise"] and not hour == self.just_executed:
      self.just_executed = hour
      self.homeware.execute("scene_astro_day","enable",True)
    elif hour == self.astro_data["sunset"] and not hour == self.just_executed:
      self.just_executed = hour
      if self.homeware.get("scene_winter", "enable"):
        self.homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
      self.homeware.execute("scene_astro_day","enable",False)

    # Reset the last just_executed block
    if not self.just_executed == hour:
      self.just_executed = ""

  def _publish_heartbeat_if_due(self):
    if time.time() - self.last_heartbeat_timestamp > 10:
      self.mqtt_client.publish(HEARTBEAT_TOPIC, self.settings.service_id)
      self.last_heartbeat_timestamp = time.time()
