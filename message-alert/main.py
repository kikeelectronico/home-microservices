import paho.mqtt.client as mqtt
import telebot
import os

from logger import Logger

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "no_set")
ENRIQUE_CHAT_ID = os.environ.get("ENRIQUE_CHAT_ID", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
TOPICS = ["heartbeats/request","message-alerts"]
SERVICE = "message-alert-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
bot = telebot.TeleBot(token=BOT_TOKEN)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc):
    for topic in TOPICS:
        client.subscribe(topic)

# Do tasks when a message is received
def on_message(client, userdata, msg):
  if msg.topic == "heartbeats/request":
    # Send heartbeat
    mqtt_client.publish("heartbeats", "message-alert")
  else:
    # Send the message to the Telegram API
    payload = msg.payload.decode('utf-8').replace("\'", "\"")
    bot.send_message(ENRIQUE_CHAT_ID, payload)
	
# Main entry point
if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    #logger.log(message, severity="ERROR")
    exit()
  if MQTT_USER == "no_set":
    report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set":
    report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set":
    report("MQTT_HOST env vars no set")
  if BOT_TOKEN == "no_set":
    report("BOT_TOKEN env vars no set")
  if ENRIQUE_CHAT_ID == "no_set":
    report("ENRIQUE_CHAT_ID env vars no set")

  # Declare the callback functions
  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting", severity="INFO")
  # Main loop
  mqtt_client.loop_forever()

    