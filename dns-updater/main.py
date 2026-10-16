import requests
from requests.exceptions import ConnectTimeout, ConnectionError
import time
import paho.mqtt.client as mqtt
import logging
from constants import HEARTBEAT_TOPIC, MQTT_PORT, REQUEST_TIMEOUT, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_ip = "unknown"
settings = None
mqtt_client = None

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

def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  register_shutdown_handlers()
  global last_ip
  global settings
  global mqtt_client
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

  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  # Main loop
  while not stop_requested():
    # Get current public IP
    try:
      ip = requests.get(settings.get_ip_endpoint, timeout=REQUEST_TIMEOUT).text
      # Verify if the API has changed
      if not ip == last_ip and len(ip.split(".")) == 4:
        # Homeware
        # Make an update request to the Cloudflare API
        url = "https://api.cloudflare.com/client/v4/zones/" + settings.cloudflare_zone + "/dns_records/" + settings.cloudflare_dns_id
        payload="{\"content\": \"" + ip + "\"}"
        headers = {
          'Authorization': 'Bearer ' + settings.cloudflare_token,
          'Content-Type': 'application/json'
        }
        response = requests.request("PATCH", url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT).json()
        # Verify the response from Cloudflare
        if response["success"]:
          logging.info("IP de Homeware actualizada")
        else:
          logging.error("Problemas al actualizar la IP de Homeware")
          mqtt_client.publish("notificacion/text/alert", "Problemas al actualizar la IP de Homeware")
        last_ip = ip
      # Send heartbeat
      mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)
    except ConnectTimeout as e:
      logging.info("Connection timeout")
    except ConnectionError as e:
      logging.info("Connection error")
    finally:
      # Wait until next iteration
      wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
    
