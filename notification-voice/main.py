import logging

from mqtt import set_mqtt_client
from constants import TOPICS
from Homeware import Homeware
from Voice import Voice
from service import NotificationVoiceService
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Main entry point
def main():
  # Register shutdown handlers
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()

  logging.basicConfig(
    level=logging.INFO,
    format=(
      "%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
      if settings.env == "dev"
      else "%(message)s"
    )
  )
  logging.info("Starting %s", settings.service_id)

  service = NotificationVoiceService()

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host_network,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=TOPICS,
    message_handler=service._handle_message
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  voice = Voice(homeware)
  service.initialize(homeware, voice)

  # Wake up alert
  try:
    service.send_wakeup_message()

    # Main loop
    mqtt_client.loop_start()
    while not stop_requested():
      wait_for_stop(1)
  finally:
    # Clean shutdown
    logging.info("Disconnecting from the MQTT broker.")
    try:
      mqtt_client.loop_stop()
    finally:
      try:
        mqtt_client.disconnect()
      finally:
        logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
