import paho.mqtt.client as mqtt
import functions
import logging

from constants import BLOCK_TIME, HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None

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
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()
  logging.info("Starting %s", settings.service_id)

  # Instantiate objects
  mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=settings.service_id,
    protocol=mqtt.MQTTv5
  )

  # Connect to the mqtt broker
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
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
    
