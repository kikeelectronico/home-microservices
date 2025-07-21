import paho.mqtt.client as mqtt
import datetime
import os
import time
import requests
import json

from homeware import Homeware
from Alert import Alert
from logger import Logger

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
WHEATHER_API_KEY = os.environ.get("WHEATHER_API_KEY", "no_set")
WHEATHER_QUERY = os.environ.get("WHEATHER_QUERY", "no_set")
ENV = os.environ.get("ENV", "dev")


# Define constants
MQTT_PORT = 1883
SERVICE = "timer-" + ENV

# Declare variables
last_heartbeat_timestamp = 0
just_executed = ""
astro_data = {
  "sunset": ""
}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, SERVICE)
alert = Alert(mqtt_client, SERVICE)

def updateAstroData():
  try:
    url = "https://api.weatherapi.com/v1/astronomy.json?key=" + WHEATHER_API_KEY   + "&q=" + WHEATHER_QUERY
    response = requests.request("GET", url, verify=False, timeout=5)
    if response.status_code == 200:
      global astro_data
      data = response.json()
      sunset = data["astronomy"]["astro"]["sunset"].split(" ")[0]
      sunset = str(int(sunset.split(":")[0]) + 12) + ":" + sunset.split(":")[1] + ":00"
      sunrise = data["astronomy"]["astro"]["sunrise"].split(" ")[0]
      sunrise = str(int(sunrise.split(":")[0])) + ":" + sunrise.split(":")[1] + ":00"
      astro_data = {
        "sunrise": sunrise,
        "sunset": sunset
      }
    else:
      logger.log("Fail to update weather data. Status code: " + str(response.status_code), severity="WARNING")
  except (requests.ConnectionError, requests.Timeout) as exception:
    logger.log("Fail to update weather data. Conection error.", severity="WARNING")


def main():
  global last_heartbeat_timestamp
  global just_executed
  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if WHEATHER_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if WHEATHER_QUERY == "no_set": report("HOMEWARE_API_KEY env vars no set")

  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  today = datetime.datetime.now()
  hour = today.strftime("%H:%M:%S")
  logger.log("Starting " + SERVICE , severity="INFO")
  logger.log("Hora local " + str(hour), severity="INFO")
  # Get astro data
  updateAstroData()
  # Main loop
  while True:
    # Get current time
    today = datetime.datetime.now()
    minute = today.strftime("%M")
    if minute == "05":
      homeware.execute("switch_hood", "on", True)
    elif minute == "15":
      homeware.execute("switch_hood", "on", False)
    hour = today.strftime("%H:%M:%S")
    # Time blocks
    # if hour == "03:00:00" and not hour == just_executed:
    #   just_executed = hour
    #   homeware.execute("hue_8", "on", False)
    if hour == "04:00:00" and not hour == just_executed:
      just_executed = hour
      updateAstroData()
    # elif hour == "06:00:00" and not hour == just_executed:
    #   just_executed = hour
    #   homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    # elif hour == "07:00:00" and not hour == just_executed:
    #   just_executed = hour
    #   homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    elif hour == "07:30:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("scene_winter", "enable"):
          homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21)
          homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
          homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
          homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
    elif hour == "08:00:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("scene_summer", "enable"):
          homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 26.5)
          # homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    elif hour == "08:55:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        alert.voice("5 minutos para las nueve.")
      homeware.execute("hue_5", "color", {"temperatureK": 4000})
    elif hour == "09:00:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("scene_winter", "enable"):
          homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 20)
          homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
        # elif homeware.get("scene_summer", "enable"):
        #   homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    elif hour == "10:00:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if (weekday in [5,6] or homeware.get("scene_on_vacation", "enable")) and homeware.get("switch_at_home", "on"):
        if homeware.get("scene_winter", "enable"):
          homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21)
          homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
          homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          homeware.execute("thermostat_livingroom", "thermostatMode", "heat")
          homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
          homeware.execute("thermostat_bathroom", "thermostatMode", "heat")
    elif hour == "10:30:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness") < 20 and homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          alert.voice("Poca luz.")
    elif hour == "12:00:00" and not hour == just_executed:
      just_executed = hour
      if homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("scene_dim", "enable") and homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          alert.voice("Luz indirecta activada.")
      weekday = today.weekday()
      if (weekday in [5,6] or homeware.get("scene_on_vacation", "enable")) and homeware.get("switch_at_home", "on"):
        if homeware.get("scene_winter", "enable"):
          homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 20)
          homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
          homeware.execute("thermostat_bathroom", "thermostatTemperatureSetpoint", 21)
    elif hour == "16:00:00" and not hour == just_executed:
      just_executed = hour
      weekday = today.weekday()
      if weekday in [0,1,2,3,4] and homeware.get("switch_at_home", "on") and (not homeware.get("scene_on_vacation", "enable")):
        if homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness") < 20 and homeware.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "occupancy") == "OCCUPIED":
          alert.voice("Poca luz.")
    elif hour == "21:00:00" and not hour == just_executed:
      just_executed = hour
      homeware.execute("hue_5", "color", {"temperatureK": 2700})
    elif hour == "22:00:00" and not hour == just_executed:
      just_executed = hour
      if homeware.get("scene_winter", "enable"):
        homeware.execute("thermostat_dormitorio", "thermostatTemperatureSetpoint", 19)
        homeware.execute("thermostat_dormitorio", "thermostatMode", "heat")
        homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 21)
        homeware.execute("thermostat_bathroom", "thermostatMode", "off")
      homeware.execute("scene_dim","enable",True)
    elif hour == "23:00:00" and not hour == just_executed:
      just_executed = hour
      if homeware.get("scene_winter", "enable"):
        homeware.execute("thermostat_livingroom", "thermostatMode", "off")

    #Astro time blocks
    if hour == "0" + astro_data["sunrise"] and not hour == just_executed:
      just_executed = hour
      homeware.execute("scene_astro_day","enable",True)
    elif hour == astro_data["sunset"] and not hour == just_executed:
      just_executed = hour
      if homeware.get("scene_winter", "enable"):
        homeware.execute("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)
      homeware.execute("scene_astro_day","enable",False)

    # Reset the last just_executed block
    if not just_executed == hour:
      just_executed = ""

    # Send the heartbeat
    if time.time() - last_heartbeat_timestamp > 10:
      mqtt_client.publish("heartbeats", SERVICE)
      last_heartbeat_timestamp = time.time()
    
    time.sleep(0.1)

# Main entry point
if __name__ == "__main__":
  main()
      