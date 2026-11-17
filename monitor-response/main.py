import logging

from google.cloud import bigquery

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, SLEEP_TIME
from service import MonitorResponseService
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Main entry point
def main():
  # Register shutdown handlers
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()

  # Configure logging
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
  bigquery_client = bigquery.Client()
  mqtt_client = None
  try:
    service = MonitorResponseService(settings, bigquery_client)

    mqtt_client = set_mqtt_client(
      settings.mqtt_host,
      settings.mqtt_port,
      settings.mqtt_user,
      settings.mqtt_pass,
      settings.service_id,
      subscriptions=[settings.response_test_trigger_topic, settings.response_test_response_topic],
      message_handler=service._handle_message
    )

    # Main loop
    mqtt_client.loop_start()
    while not stop_requested():
      mqtt_client.publish(HEARTBEAT_TOPIC, "are-you-there")
      wait_for_stop(SLEEP_TIME)
  finally:
    try:
      if mqtt_client is not None:
        # Clean shutdown
        logging.info("Disconnecting from the MQTT broker.")
        try:
          mqtt_client.loop_stop()
        finally:
          mqtt_client.disconnect()
    finally:
      bigquery_client.close()
      logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
