import json
import logging

from homeware import Homeware
from mqtt import set_mqtt_client
from service import BLEInboundService
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

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host_network,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  service = BLEInboundService()
  service.initialize(
    homeware,
    mqtt_client,
    json.loads(settings.ble_sensors),
    json.loads(settings.ble_presence)
  )

  logging.info("Starting " + settings.service_id)
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
