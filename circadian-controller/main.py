import datetime
import time
import requests
import math
import logging

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC
from homeware import Homeware
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
just_executed = False
settings = None
mqtt_client = None
homeware = None
solar_cycle = {
  "sunset": 0,
  "sunrise": 0
}

def updateSolarData():
  try:
    url = "https://api.weatherapi.com/v1/astronomy.json?key=" + settings.wheather_api_key + "&q=" + settings.wheather_query
    response = requests.get(url, timeout=5)
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
  global settings
  global mqtt_client
  global homeware
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  register_shutdown_handlers()
  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting %s", settings.service_id)

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)

  mqtt_client.loop_start()
  today = datetime.datetime.now()
  hour = today.strftime("%H:%M:%S")
  logging.info("Hora local " + str(hour))
  # Get astro data
  updateSolarData()
  # Main loop
  while not stop_requested():
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
      homeware.execute("hue_1", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_4", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_5", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_6", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_9", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_10", "color", {"temperatureK": color_temperature})
      if not homeware.get("hue_15", "currentToggleSettings")["emergencia"]:
        homeware.execute("hue_15", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_16", "color", {"temperatureK": color_temperature})
      homeware.execute("hue_17", "color", {"temperatureK": color_temperature})

    # Send the heartbeat
    if time.time() - last_heartbeat_timestamp > 10:
      mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)
      last_heartbeat_timestamp = time.time()
    
    wait_for_stop(55)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

# Main entry point
if __name__ == "__main__":
  main()
      
