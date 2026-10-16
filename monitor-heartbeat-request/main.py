import logging

from mqtt import set_mqtt_client
from constants import HEARTBEAT_REQUEST_TOPIC, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None

# Main entry point
if __name__ == "__main__":
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
  mqtt_client.loop_start()
  # Wake up alert
  while not stop_requested():
    # Send the heartbeat request and wait
    mqtt_client.publish(HEARTBEAT_REQUEST_TOPIC, "are-you-there")
    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")
      
