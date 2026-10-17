import logging

from constants import SLEEP_TIME, HEARTBEAT_TOPIC, RULES
from homeware import Homeware
from mqtt import set_mqtt_client
from service import MonitorCauseEffectService
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
  logging.info(f"Starting {settings.service_id}.")

  # Create mqtt client
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  
  # Create homeware object
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  service = MonitorCauseEffectService(homeware, mqtt_client, RULES)

  # Main loop
  try:
    mqtt_client.loop_start()
    while not stop_requested():
      # Evaluate rules
      service.evaluate_rules()

      # Send heartbeat
      mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

      # Wait until next iteration
      wait_for_stop(SLEEP_TIME)
  finally:
    # Clean shutdown
    logging.info("Disconnecting from the MQTT broker.")
    try:
      mqtt_client.loop_stop()
    finally:
      mqtt_client.disconnect()
    logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
