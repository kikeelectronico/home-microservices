import time
import logging

from mqtt import set_mqtt_client
from constants import MQTT_PORT, TOPICS
from Homeware import Homeware
from Voice import Voice
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
homeware = None
voice = None


def handle_message(topic, payload):
  if topic == TOPICS[0]:
    # Send the message to the Smart Speakers
    if homeware.get("scene_awake", "enable"):
      payload = payload.decode('utf-8')
      voice.getAndPlay(payload)
  elif topic == TOPICS[0]:
    # Send the message to the Smart Speakers
    payload = payload.decode('utf-8')
    voice.getAndPlay(payload)

# Main entry point
if __name__ == "__main__":
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
    settings.mqtt_host_network,
    MQTT_PORT,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=TOPICS,
    message_handler=handle_message
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  voice = Voice(homeware)
  
  # Wake up alert
  hour = int(time.strftime("%H"))
  message = ""
  if hour >= 22 or (hour >= 0 and hour < 7):
    message = "buenas noches. Ya estoy preparada."
  elif hour >= 7 and hour < 15:
    message = "buenos días. Ya estoy preparada."
  elif hour >= 15 and hour < 22:
    message = "buenas tardes. Ya estoy preparada."
  voice.getAndPlay(message)
  # Main loop
  mqtt_client.loop_start()
  while not stop_requested():
    wait_for_stop(1)

  # Clean shutdown
  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")


    
