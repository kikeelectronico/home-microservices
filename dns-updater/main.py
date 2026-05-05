import requests
import os
import time
import paho.mqtt.client as mqtt
import logging

# Load env vars
if os.environ.get("GET_IP_ENDPOINT", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

GET_IP_ENDPOINT = os.environ.get("GET_IP_ENDPOINT", "no_set")
CLOUDFLARE_ZONE = os.environ.get("CLOUDFLARE_ZONE", "no_set")
CLOUDFLARE_DNS_ID = os.environ.get("CLOUDFLARE_DNS_ID", "no_set")
CLOUDFLARE_DNS_ID_PB = os.environ.get("CLOUDFLARE_DNS_ID_PB", "no_set")
CLOUDFLARE_TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "no_set")
MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SLEEP_TIME = 10
SERVICE = "dns-updater-" + ENV

# Declare variables
last_ip = "unknown"

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)

def main():
  global last_ip
  # Check env vars
  def report(message):
    print(message)
    exit()
  if GET_IP_ENDPOINT == "no_set": report("GET_IP_ENDPOINT env vars no set")
  if CLOUDFLARE_ZONE == "no_set": report("CLOUDFLARE_ZONE env vars no set")
  if CLOUDFLARE_DNS_ID == "no_set": report("CLOUDFLARE_DNS_ID env vars no set")
  if CLOUDFLARE_DNS_ID_PB == "no_set": report("CLOUDFLARE_DNS_ID_PB env vars no set")
  if CLOUDFLARE_TOKEN == "no_set": report("CLOUDFLARE_TOKEN env vars no set")
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")

  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logging.info("Starting " + SERVICE)
  # Main loop
  while True:
    # Get current public IP
    ip = requests.get(GET_IP_ENDPOINT).text
    # Verify if the API has changed
    if not ip == last_ip and len(ip.split(".")) == 4:
      # Homeware
      # Make an update request to the Cloudflare API
      url = "https://api.cloudflare.com/client/v4/zones/" + CLOUDFLARE_ZONE + "/dns_records/" + CLOUDFLARE_DNS_ID
      payload="{\"content\": \"" + ip + "\"}"
      headers = {
        'Authorization': 'Bearer ' + CLOUDFLARE_TOKEN,
        'Content-Type': 'application/json'
      }
      response = requests.request("PATCH", url, headers=headers, data=payload).json()
      # Verify the response from Cloudflare
      if response["success"]:
        logging.info("IP de Homeware actualizada")
      else:
        logging.error("Problemas al actualizar la IP de Homeware")
        mqtt_client.publish("message-alerts", "Problemas al actualizar la IP de Homeware")
      # PB
      # Make an update request to the Cloudflare API
      url = "https://api.cloudflare.com/client/v4/zones/" + CLOUDFLARE_ZONE + "/dns_records/" + CLOUDFLARE_DNS_ID_PB
      payload="{\"content\": \"" + ip + "\"}"
      headers = {
        'Authorization': 'Bearer ' + CLOUDFLARE_TOKEN,
        'Content-Type': 'application/json'
      }
      response = requests.request("PATCH", url, headers=headers, data=payload).json()
      # Verify the response from Cloudflare
      if response["success"]:
        logging.info("IP de PB actualizada")
      else:
        logging.error("Problemas al actualizar la IP de PB")
        mqtt_client.publish("message-alerts", "Problemas al actualizar la IP de PB")
      last_ip = ip
    # Send heartbeat
    mqtt_client.publish("heartbeats", SERVICE)
    # Wait until next iteration
    time.sleep(SLEEP_TIME)

if __name__ == "__main__":
  main()
    