import logging

from constants import SLEEP_TIME, HEARTBEAT_TOPIC, RULES
from homeware import Homeware
from mqtt import set_mqtt_client
from rules import evaluateRules
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Create vars for objects
mqtt_client = None 
homeware = None
settings = None

# Main entry point
if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )

  # Register shutdown handlers
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
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

  # Main loop
  while not stop_requested():
    # Evaluate rules
    evaluateRules(homeware, mqtt_client, RULES)

    # Send heartbeat
    mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)

    # Wait until next iteration
    wait_for_stop(SLEEP_TIME)

  # Clean shutdown
  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

    
