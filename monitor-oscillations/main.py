import logging

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, PARAMS, SLEEP_TIME
from service import MonitorOscillationsService
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

  service = MonitorOscillationsService()

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=[HEARTBEAT_TOPIC] + [f"device/{topic}" for topic in PARAMS],
    message_handler=service._handle_message
  )
  service.initialize(mqtt_client)
  try:
    mqtt_client.loop_start()
    while not stop_requested():
      mqtt_client.publish(HEARTBEAT_TOPIC, "are-you-there")
      wait_for_stop(SLEEP_TIME)
  finally:
    logging.info("Disconnecting from the MQTT broker.")
    try:
      mqtt_client.loop_stop()
    finally:
      mqtt_client.disconnect()
    logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
