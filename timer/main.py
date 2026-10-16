import paho.mqtt.client as mqtt
import datetime
import time
import requests
import json
import logging

from homeware import Homeware
from Alert import Alert
from constants import HEARTBEAT_TOPIC, MQTT_PORT
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
just_executed = ""
settings = None
mqtt_client = None
homeware = None
alert = None
astro_data = {
  "sunset": 0,
  "sunrise": 0
}

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        wait_for_stop(5)

def updateAstroData():
  try:
    url = "https://api.weatherapi.com/v1/astronomy.json?key=" + settings.wheather_api_key + "&q=" + settings.wheather_query
    response = requests.get(url, timeout=5)
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
      logging.warning("Fail to update weather data. Status code: " + str(response.status_code))
  except (requests.ConnectionError, requests.Timeout) as exception:
    logging.warning("Fail to update weather data. Conection error.")


def main():
  global last_heartbeat_timestamp
  global just_executed
  global settings
  global mqtt_client
  global homeware
  global alert
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
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  alert = Alert(mqtt_client)

  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  today = datetime.datetime.now()
  hour = today.strftime("%H:%M:%S")
  logging.info("Hora local " + str(hour))
  # Get astro data
  updateAstroData()
  # Main loop
  while not stop_requested():
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
      homeware.execute("scene_circadian_controller_enable", "enable", True)
    # elif hour == "06:00:00" and not hour == just_executed:
    #   just_executed = hour
    #   homeware.execute("thermostat_livingroom", "thermostatMode", "cool")
    # elif hour == "07:00:00" and not hour == just_executed:
    #   just_executed = hour
    #   homeware.execute("thermostat_livingroom", "thermostatMode", "off")
    elif hour == "08:30:00" and not hour == just_executed:
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
      mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)
      last_heartbeat_timestamp = time.time()
    
    wait_for_stop(0.1)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

# Main entry point
if __name__ == "__main__":
  main()
      
