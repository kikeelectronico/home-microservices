import functions
import logging

from mqtt import set_mqtt_client
from constants import BLOCK_TIME, HEARTBEAT_TOPIC, SLEEP_TIME
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

  # Main loop
  while not stop_requested():
    # Verify Homeware connectivity
    if not functions.homewareTest(settings.homeware_api_url, settings.homeware_api_key):
      logging.warning("Homeware no responde")
      mqtt_client.publish("notificacion/voice/alert", "Homeware no responde")
      mqtt_client.publish("notificacion/text/alert", "Homeware no responde")
      wait_for_stop(BLOCK_TIME)
    if stop_requested():
      break
    # Verify Hue Bridge connectivity
    if not functions.hueTest(settings.hue_host, settings.hue_token):
      logging.warning("Hue bridge no responde")
      mqtt_client.publish("notificacion/voice/alert", "Hue bridge no responde")
      mqtt_client.publish("notificacion/text/alert", "Hue bridge no responde")
      wait_for_stop(BLOCK_TIME)
    if stop_requested():
      break
    # Verify Ikea Bridge connectivity
    if not functions.ikeaTest(settings.ikea_host, settings.ikea_token):
      logging.warning("Ikea bridge no responde")
      mqtt_client.publish("notificacion/voice/alert", "Ikea bridge no responde")
      mqtt_client.publish("notificacion/text/alert", "Ikea bridge no responde")
      wait_for_stop(BLOCK_TIME)
    if stop_requested():
      break
    # Send heartbeat
    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)
    # Wait until next iteration
    wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")
    
