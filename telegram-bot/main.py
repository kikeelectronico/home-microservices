import telebot
import logging
import threading
from google.cloud import storage

import functions
from settings import Settings
from shutdown import register_shutdown_handlers, wait_for_stop

settings = None
bot = None
storage_client = None

# Commands handler
def send_welcome(message):
  command = message.text.split()[0]

  if command == '/start':
    bot.reply_to(message, "Hi, I am Maguna")
  elif command == '/help':
    bot.reply_to(message, "I am sorry but I don't know you.")
  else:
    if str(message.from_user.id) == settings.enrique_chat_id:
        if command == '/test':
            # Test an authenticated command
            response = functions.test()
            bot.send_message(settings.enrique_chat_id, response, parse_mode='Markdown')
        elif command == '/home':
            # Test Homeware API and db
            response = functions.getHomewareTest(settings.homeware_api_url, settings.homeware_api_key)
            bot.send_message(settings.enrique_chat_id, "Corriendo" if response else "Caido", parse_mode='Markdown')
        elif command == '/directions':
            # Get the public IP
            response = functions.getPublicIP(settings.get_ip_endpoint)
            bot.send_message(settings.enrique_chat_id, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "I am sorry but I don't know you.")

# Global handler
def echo_message(message):
    if str(message.from_user.id) == settings.enrique_chat_id:
        # Download the YouTube video once the URL is given
        if "youtube.com" in message.text or "youtu.be" in message.text:
            bot.send_message(settings.enrique_chat_id, "Descargando...", parse_mode='Markdown')
            url = message.text
            urls = functions.downloadYouTubeVideo(url, storage_client, settings.bucket_name)
            bot.send_message(settings.enrique_chat_id, "Lo tenemos", parse_mode='Markdown')
            for url in urls:
                bot.send_message(settings.enrique_chat_id, url, parse_mode='Markdown')

def register_handlers():
    bot.message_handler(commands=['start', 'help','test','home','directions'])(send_welcome)
    bot.message_handler(func=lambda message: True)(echo_message)


# Main entry point
def main():
    global settings
    global bot
    global storage_client
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
    register_handlers()

    # Main loop
    polling_thread = threading.Thread(target=bot.infinity_polling)
    polling_thread.start()
    while not wait_for_stop(1):
        pass

    bot.stop_polling()
    polling_thread.join()
    storage_client.close()
    logging.info("Shutdown completed.")

if __name__ == "__main__":
    main()
