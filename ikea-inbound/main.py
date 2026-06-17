import paho.mqtt.client as mqtt
import os
import time
import json
import ssl
import threading
import uuid
from websocket import WebSocketApp
import logging

from homeware import Homeware
import devices

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
WEBSOCKET_RECONNECT_DELAY = 5

# Variables
tasks = {}

# Instantiate objects
mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

voltages_map = {}

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, rc, properties):
  if rc != 0:
    logging.warning("Unexpected MQTT disconnection (rc=%s). Reconnecting...", rc)
    while True:
      try:
        client.reconnect()
        logging.info("Reconnected to MQTT broker")
        break
      except Exception as exc:
        logging.warning("Reconnect failed: %s", exc)
        time.sleep(5)

def on_message(ws, message):
  try:
    event = json.loads(message)
  except (json.JSONDecodeError, TypeError):
    logging.warning("Invalid IKEA WebSocket JSON payload: %r", message)
    return
  if not isinstance(event, dict):
    logging.warning("Invalid IKEA WebSocket event type: %r", event)
    return
  data = event.get("data")
  if not isinstance(data, dict):
    logging.warning("Invalid IKEA WebSocket event data type: %r", event)
    return
  attributes = data.get("attributes")
  if not isinstance(attributes, dict):
    logging.warning("Invalid IKEA WebSocket attributes type: %r", data)
    return
  
  # The action depends on deviceType
  if data.get("deviceType") == "outlet":
    devices.outlet(data, homeware)
  elif data.get("deviceType") == "motionSensor":
    devices.motionSensor(data, homeware)
  elif data.get("deviceType") == "airPurifier":
    devices.airPurifier(data, homeware)
  elif data.get("deviceType") == "environmentSensor":
    devices.environmentSensor(data, homeware)

  # Loop over pending tasks
  for task_id in list(tasks.keys()):
    task = tasks[task_id]
    if (time.time() - task["time"]) > 10:
      homeware.execute(task["device_id"], task["param"], task["value"])
      del tasks[task_id]


def on_error(ws, error):
  logging.warning("Error: " + error)

def on_close(ws, close_status_code, close_msg):
  logging.info("Conexión cerrada")

def on_open(ws):
  logging.info("Conexión abierta")

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
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )
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
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)
  
  # Open WebSocket
  url = f"wss://{IKEA_HOST}:8443/v1"
  headers = {
    "Authorization": "Bearer " + IKEA_TOKEN
  }
  # Contexto SSL para certificado autofirmado
  sslopt = {"cert_reqs": ssl.CERT_NONE}
  while True:
    ws_app = WebSocketApp(
      url,
      header=[key + ": " + value for key, value in headers.items()],
      on_message=on_message,
      on_error=on_error,
      on_close=on_close,
      on_open=on_open,
    )
    try:
      ws_app.run_forever(sslopt=sslopt)
    except Exception as exc:
      logging.warning("IKEA WebSocket stopped with error: %s", exc)
    logging.warning("IKEA WebSocket disconnected. Reconnecting in %ss", WEBSOCKET_RECONNECT_DELAY)
    time.sleep(WEBSOCKET_RECONNECT_DELAY)
