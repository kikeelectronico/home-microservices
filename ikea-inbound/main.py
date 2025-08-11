import paho.mqtt.client as mqtt
import os
import time
import json
import ssl
import threading
import time
import uuid
from websocket import WebSocketApp

from homeware import Homeware
from logger import Logger

import urllib3
urllib3.disable_warnings()

# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
IKEA_HOST = os.environ.get("IKEA_HOST", "no_set")
IKEA_TOKEN = os.environ.get("IKEA_TOKEN", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "ikea-inbound-" + ENV
OUTLET_CURRENT_THRESHOLD = 0.1


# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
logger = Logger(mqtt_client, SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY, logger)

def on_message(ws, message):
  event = json.loads(message)
  # print(event)
  data = event["data"]
  if data["type"] == "outlet":
    if "isReachable" in data:
      homeware.execute(data["id"], "online", data["isReachable"])
    if "isOn" in data["attributes"]:
      homeware.execute(data["id"], "on", data["attributes"]["isOn"])
    if "currentAmps" in data["attributes"]:
      homeware.execute(data["id"], "isRunning", data["attributes"]["currentAmps"] > OUTLET_CURRENT_THRESHOLD)

def on_error(ws, error):
  logger.log("Error: " + error , severity="WARNING")

def on_close(ws, close_status_code, close_msg):
  logger.log("Conexión cerrada", severity="INFO")

def on_open(ws):
  logger.log("Conexión abierta", severity="INFO")

  def run():
    while True:
      ping_msg = {
        "id": str(uuid.uuid4()),
        "specversion": "1.1.0",
        "source": "urn:lpgera:dirigera",
        "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "type": "ping",
        "data": None
      }
      ws.send(json.dumps(ping_msg))
      time.sleep(30)

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

# Main entry point
if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    exit()

  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if IKEA_HOST == "no_set": report("IKEA_HOST env vars no set")
  if IKEA_TOKEN == "no_set": report("IKEA_TOKEN env vars no set")
  
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logger.log("Starting " + SERVICE , severity="INFO")
  
  # Open WebSocket
  url = f"wss://{IKEA_HOST}:8443/v1"
  headers = {
    "Authorization": "Bearer " + IKEA_TOKEN
  }
  ws_app = WebSocketApp(
    url,
    header=[key + ": " + value for key, value in headers.items()],
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open,
  )

  # Contexto SSL para certificado autofirmado
  sslopt = {"cert_reqs": ssl.CERT_NONE}
  ws_app.run_forever(sslopt=sslopt)
