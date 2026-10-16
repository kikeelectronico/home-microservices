import time
import pychromecast
import logging

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, MQTT_PORT
from homeware import Homeware
import logic
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
last_heartbeat_timestamp = 0
settings = None
mqtt_client = None
homeware = None

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
)

# Main entry point
if __name__ == "__main__":
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting " + settings.service_id)

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host_network,
    MQTT_PORT,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  
  mqtt_client.loop_start()

  device = None
  browser = None
  while not stop_requested():
    try:
      # Connect to the tv
      chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Tele"])
      if not chromecasts:
            raise Exception("Chromecast not found")
      device = chromecasts[0]
      device.wait()
      device_controller = device.media_controller
      # device_controller.block_until_active(5)
      while device.socket_client.is_connected and not stop_requested():
        # if device.app_display_name is not None:
        if device_controller.status.player_state in ["IDLE", "UNKNOWN", "PAUSED"]:
          logic.notPlayingLights(homeware)
        if device_controller.status.player_state == "PLAYING":
          logic.playingLights(homeware)

          # Send the heartbeat
          if time.time() - last_heartbeat_timestamp > 10:
            mqtt_client.publish(HEARTBEAT_TOPIC, settings.service_id)
            last_heartbeat_timestamp = time.time()
          
        wait_for_stop(5)
    except Exception:
        try:
            device.disconnect()
        except Exception:
            logging.info("Fail to force disconnect.")
        try:
            browser.stop_discovery()
        except Exception:
            logging.info("Fail to stop discovery.")

        logging.info("Chromecast connection lost. Reconnecting in 10s.")
        wait_for_stop(10)

  try:
    if device is not None:
      device.disconnect()
  except Exception:
    logging.info("Fail to force disconnect.")
  try:
    if browser is not None:
      browser.stop_discovery()
  except Exception:
    logging.info("Fail to stop discovery.")

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")
