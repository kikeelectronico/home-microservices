import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ElementTree
import re
from datetime import date, datetime, timedelta
import os
import time
import requests
import logging
import json

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
AEMET_RSS = os.environ.get("AEMET_RSS", "no_set")
AEMET_AREA = os.environ.get("AEMET_AREA", "no_set")
ENV = os.environ.get("ENV", "dev")


# Define constants
MQTT_PORT = 1883
SERVICE = "timer-" + ENV
REQUEST_TIMEOUT = 10

# Declare variables
last_heartbeat_timestamp = 0
last_build_date = ""

# Instantiate objects
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)

def relative_day(texto: str) -> int:
    match = re.search(r"\b(\d{2}-\d{2}-\d{4})\b", texto)

    if not match:
        return -1

    target_date = datetime.strptime(match.group(1), "%d-%m-%Y").date()

    return (target_date - date.today()).days

def is_alert_active(text: str) -> bool:
    pattern = (
        r"de\s+(\d{2}:\d{2})\s+(\d{2}-\d{2}-\d{4}).*?"
        r"a\s+(\d{2}:\d{2})\s+(\d{2}-\d{2}-\d{4})"
    )

    match = re.search(pattern, text)

    if not match:
        return False

    start_time, start_date, end_time, end_date = match.groups()

    start_dt = datetime.strptime(
        f"{start_date} {start_time}",
        "%d-%m-%Y %H:%M"
    )

    end_dt = datetime.strptime(
        f"{end_date} {end_time}",
        "%d-%m-%Y %H:%M"
    )

    now = datetime.now()

    return start_dt <= now <= end_dt

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while True:
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        time.sleep(5)

def main():
  global last_heartbeat_timestamp
  global last_build_date
  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if AEMET_RSS == "no_set": report("AEMET_RSS env vars no set")
  if AEMET_AREA == "no_set": report("AEMET_AREA env vars no set")

  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)
  # Main loop
  while True:
    
    # Get AEMET RSS feed
    data = None
    url = AEMET_RSS
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        data = response.text
    else:
      logging.warning("Fail to get AEMET RSS feed. Status code: " + str(response.status_code))

    # Manipulate data
    if data:
      root = ElementTree.fromstring(data)
      build_date = root.find("channel").find("lastBuildDate").text
      if build_date != last_build_date:
        for item in root.find("channel").findall("item"):
          title = item.find("title").text
          if AEMET_AREA in title:
            description = item.find("description").text
            days_delta = relative_day(description)
            is_active = is_alert_active(description)
            warning = {
              "title": title.split(" Metropolitana y Henares")[0],
              "days_delta": days_delta,
              "is_active": is_active,
              "build_date": build_date
            }
            mqtt_client.publish("meteo/warnings", json.dumps(warning))
        print("build_date", build_date)
        last_build_date = build_date

    # Send the heartbeat
    if time.time() - last_heartbeat_timestamp > 10:
      mqtt_client.publish("heartbeats", SERVICE)
      last_heartbeat_timestamp = time.time()
    
    time.sleep(1800)

# Main entry point
if __name__ == "__main__":
  main()
      
