import logging

from mqtt import set_mqtt_client
from hue import Hue
from service import HueOutboundService
from settings import Settings
from shutdown import register_shutdown_handlers

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

  # Instantiate objects
  hue = Hue(settings.hue_host, settings.hue_token)
  service = HueOutboundService(hue)
  service.initialize()
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=service.topics,
    message_handler=service._handle_message
  )

  try:
    mqtt_client.loop_start()
    service.run()
  finally:
    logging.info("Disconnecting from the MQTT broker.")
    try:
      mqtt_client.loop_stop()
    finally:
      mqtt_client.disconnect()
    logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
