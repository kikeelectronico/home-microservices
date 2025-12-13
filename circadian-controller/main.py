import paho.mqtt.client as mqtt
import datetime
import os
import time
import requests
import math
import logging

from homeware import Homeware

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
SERVICE = "circadian-controller-" + ENV

# Declare variables
last_heartbeat_timestamp = 0
just_executed = False
solar_cycle = {
  "sunset": ""
}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

def updateSolarData():
  try:
    url = "https://api.weatherapi.com/v1/astronomy.json?key=" + WHEATHER_API_KEY   + "&q=" + WHEATHER_QUERY
    response = requests.request("GET", url, timeout=5)
    if response.status_code == 200:
      global solar_cycle
      data = response.json()
      sunset = data["astronomy"]["astro"]["sunset"].split(" ")[0]
      sunset = int(sunset.split(":")[0]) + 12 + (int(sunset.split(":")[1])/60)
      sunrise = data["astronomy"]["astro"]["sunrise"].split(" ")[0]
      sunrise = int(sunrise.split(":")[0]) + (int(sunrise.split(":")[1])/60)
      solar_cycle = {
        "sunrise": sunrise,
        "sunset": sunset
      }
    else:
      logging.warning("Fail to update weather data. Status code: " + str(response.status_code))
  except (requests.ConnectionError, requests.Timeout) as exception:
    logging.warning("Fail to update weather data. Conection error.")

def colorTemperature(hour, sunrise, sunset, Tmin=2200, Tmax=6500):
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
  logging.info("Starting " + SERVICE)
  logging.info("Hora local " + str(hour))
  # Get astro data
  updateSolarData()
  # Main loop
  while True:
    # Get current time
    today = datetime.datetime.now()
    hour = int(today.strftime("%H"))
    minute = int(today.strftime("%M"))

    # Update astrodata
    if hour == 4 and minute == 0 and not just_executed:
      just_executed = True
      updateSolarData()
    if hour == 4 and minute == 5 and just_executed :
      just_executed = False

    # Calculate color temperature and adjust lights
    if homeware.get("scene_circadian_controller_enable", "enable"):
      color_temperature = colorTemperature((hour + (minute/60)), solar_cycle["sunrise"], solar_cycle["sunset"])
      homeware.execute("hue_5", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_6", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_9", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_10", "color", {"temperatureK": color_temperature})

    # Send the heartbeat
    if time.time() - last_heartbeat_timestamp > 10:
      mqtt_client.publish("heartbeats", SERVICE)
      last_heartbeat_timestamp = time.time()
    
    time.sleep(55)

# Main entry point
if __name__ == "__main__":
  main()
      