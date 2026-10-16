import time
import json
import ssl
import threading
import uuid
from websocket import WebSocketApp
import logging

from homeware import Homeware
import devices
from mqtt import set_mqtt_client
from constants import MQTT_PORT, WEBSOCKET_RECONNECT_DELAY
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

import urllib3
urllib3.disable_warnings()

# Variables
tasks = {}
voltages_map = {}
settings = None
mqtt_client = None
homeware = None

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
  if "lastModified" in data:
    return
  attributes = data.get("attributes")
  if not isinstance(attributes, dict):
    logging.warning("Invalid IKEA WebSocket attributes type: %r", data)
    return
  
  # The action depends on deviceType
  if data.get("deviceType") == "outlet":
    devices.outlet(data, homeware, tasks, voltages_map)
  elif data.get("deviceType") == "motionSensor":
    devices.motionSensor(data, homeware)
  elif data.get("deviceType") == "airPurifier":
    devices.airPurifier(data, homeware)
  elif data.get("deviceType") == "environmentSensor":
    devices.environmentSensor(data, homeware)
  elif data.get("deviceType") == "waterSensor":
    devices.waterLeakSensor(data, homeware)

  # Loop over pending tasks
  for task_id in list(tasks.keys()):
    task = tasks[task_id]
    if (time.time() - task["time"]) > 10:
      homeware.execute(task["device_id"], task["param"], task["value"])
      del tasks[task_id]


def on_error(ws, error):
  logging.warning("IKEA WebSocket error: %s", error)

def on_close(ws, close_status_code, close_msg):
  logging.info("IKEA WebSocket closed")

def on_open(ws):
  logging.info("IKEA WebSocket opened")

  def run():
    while not stop_requested():
      ping_msg = {
        "id": str(uuid.uuid4()),
        "specversion": "1.1.0",
        "source": "urn:lpgera:dirigera",
        "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "type": "ping",
        "data": None
      }
      try:
        ws.send(json.dumps(ping_msg))
      except Exception as exc:
        logging.warning("Fail to send IKEA WebSocket ping: %s", exc)
        break
      wait_for_stop(30)
    if stop_requested():
      ws.close()

  thread = threading.Thread(target=run)
  thread.daemon = True
  thread.start()

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
  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    MQTT_PORT,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
  
  mqtt_client.loop_start()
  
  # Open WebSocket
  url = f"wss://{settings.ikea_host}:8443/v1"
  headers = {
    "Authorization": "Bearer " + settings.ikea_token
  }
  # Contexto SSL para certificado autofirmado
  sslopt = {"cert_reqs": ssl.CERT_NONE}
  while not stop_requested():
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
    if stop_requested():
      break
    logging.warning("IKEA WebSocket disconnected. Reconnecting in %ss", WEBSOCKET_RECONNECT_DELAY)
    wait_for_stop(WEBSOCKET_RECONNECT_DELAY)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")
