import paho.mqtt.client as mqtt
import time
import pychromecast
import logging

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

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while not stop_requested():
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        wait_for_stop(5)

# Main entry point
if __name__ == "__main__":
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting " + settings.service_id)

  # Instantiate objects
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  
  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host_network, MQTT_PORT, 60, clean_start=False)
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
