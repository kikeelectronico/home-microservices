import telebot
import logging

from mqtt import set_mqtt_client
from constants import TOPICS
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
bot = None


def handle_message(topic, payload):
  # Send the message to the Telegram API
  payload = payload.decode('utf-8')
  bot.send_message(settings.enrique_chat_id, payload)
	
# Main entry point
if __name__ == "__main__":
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

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=TOPICS,
    message_handler=handle_message
  )
  bot = telebot.TeleBot(token=settings.bot_token)

  # Main loop
  mqtt_client.loop_start()
  while not stop_requested():
    wait_for_stop(1)

  # Clean shutdown
  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

    
