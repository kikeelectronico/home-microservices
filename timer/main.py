import logging

from homeware import Homeware
from Alert import Alert
from mqtt import set_mqtt_client
from service import TimerService
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
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  alert = Alert(mqtt_client)
  service = TimerService(settings, mqtt_client, homeware, alert)

  try:
    mqtt_client.loop_start()
    service.run()
  finally:
    logging.info("Disconnecting from the MQTT broker.")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
