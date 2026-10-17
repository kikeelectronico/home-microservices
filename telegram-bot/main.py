import logging
import threading

import telebot
from google.cloud import storage

from service import TelegramBotService
from settings import Settings
from shutdown import register_shutdown_handlers, wait_for_stop


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

  # Instantiate objects
  bot = telebot.TeleBot(settings.bot_token)
  storage_client = storage.Client()
  polling_thread = None
  try:
    service = TelegramBotService()
    service.initialize(settings, bot, storage_client)
    service.register_handlers()

    # Main loop
    polling_thread = threading.Thread(target=bot.infinity_polling)
    polling_thread.start()
    while not wait_for_stop(1):
      pass
  finally:
    try:
      bot.stop_polling()
    finally:
      try:
        if polling_thread is not None and polling_thread.is_alive():
          polling_thread.join()
      finally:
        storage_client.close()
        logging.info("Shutdown completed.")


if __name__ == "__main__":
  main()
