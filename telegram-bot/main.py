import telebot
import os
import logging
from google.cloud import storage

import functions

# Load env vars
if os.environ.get("BOT_TOKEN", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "no_set")
ENRIQUE_CHAT_ID = os.environ.get("ENRIQUE_CHAT_ID", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
GET_IP_ENDPOINT = os.environ.get("GET_IP_ENDPOINT", "no_set")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "no_set")

# Instantiate objects
bot = telebot.TeleBot(BOT_TOKEN)
storage_client = storage.Client()

# Commands handler
@bot.message_handler(commands=['start', 'help','test','office','home','directions','yt'])
def send_welcome(message):
  if 'start' in message.text:
    bot.reply_to(message, "Hi, I am Maguna")
  elif 'help' in message.text:
    bot.reply_to(message, "I am sorry but I don't know you.")
  else:
    if str(message.from_user.id) == ENRIQUE_CHAT_ID:
        if 'test' in message.text:
            # Test an authenticated command
            response = functions.test()
            bot.send_message(ENRIQUE_CHAT_ID, response, parse_mode='Markdown')
        elif 'home' in message.text:
            # Test Homeware API and db
            response = functions.getHomewareTest(HOMEWARE_API_URL, HOMEWARE_API_KEY)
            bot.send_message(ENRIQUE_CHAT_ID, "Corriendo" if response else "Caido", parse_mode='Markdown')
        elif 'directions' in message.text:
            # Get the public IP
            response = functions.getPublicIP(GET_IP_ENDPOINT)
            bot.send_message(ENRIQUE_CHAT_ID, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "I am sorry but I don't know you.")

# Global handler
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if str(message.from_user.id) == ENRIQUE_CHAT_ID:
        # Download the YouTube video once the URL is given
        if "youtube.com" in message.text or "youtu.be" in message.text:
            bot.send_message(ENRIQUE_CHAT_ID, "Descargando...", parse_mode='Markdown')
            url = message.text
            urls = functions.downloadYouTubeVideo(url, storage_client, BUCKET_NAME)
            bot.send_message(ENRIQUE_CHAT_ID, "Lo tenemos", parse_mode='Markdown')
            for url in urls:
                bot.send_message(ENRIQUE_CHAT_ID, url, parse_mode='Markdown')

# Main entry point
if __name__ == "__main__":
    logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
    )

    # Check env vars
    def report(message):
        print(message)
        exit()
    if BOT_TOKEN == "no_set": report("BOT_TOKEN env vars no set")
    if ENRIQUE_CHAT_ID == "no_set": report("ENRIQUE_CHAT_ID env vars no set")
    if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
    if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
    if GET_IP_ENDPOINT == "no_set": report("GET_IP_ENDPOINT env vars no set")
    if BUCKET_NAME == "no_set": report("BUCKET_NAME env vars no set")
    # Main loop
    bot.infinity_polling()
