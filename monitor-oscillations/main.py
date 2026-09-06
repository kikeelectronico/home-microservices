import logging
import os
import time
import paho.mqtt.client as mqtt

if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
ENV = os.environ.get("ENV", "dev")

MQTT_PORT = 1883
SERVICE = "monitor-oscillations-" + ENV
SLEEP_TIME = 10
OSCILLATION_THRESHOLD = 5
PARAMS = [
  "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1/on",
  "interruptor_prueba/on"
]

last_status = {}

mqtt_client = mqtt.Client(
  mqtt.CallbackAPIVersion.VERSION2,
  client_id=SERVICE,
  protocol=mqtt.MQTTv5
)

def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe("heartbeats/system", qos=1)
  for topic in PARAMS:
    client.subscribe(f"device/{topic}", qos=1)

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


def on_message(client, userdata, msg):
  global last_status

  if msg.topic == "heartbeats/system":
    for status_id in last_status:
      if last_status[status_id]["oscillating"]:
        if time.time() - last_status[status_id]["timestamp"] > OSCILLATION_THRESHOLD:
          mqtt_client.publish(f"oscillation/{status_id}", "reset")
          last_status[status_id]["counter"] = 0
          last_status[status_id]["oscillating"] = False
  else:
    topic = msg.topic
    status_id = topic.split("device/")[1]
    payload = msg.payload
    if last_status.get(status_id, None):
      if payload != last_status[status_id]["value"]:
        if time.time() - last_status[status_id]["timestamp"] < OSCILLATION_THRESHOLD:
          if last_status[status_id]["counter"] == 0:
            last_status[status_id]["counter"] = 1
          else:
            mqtt_client.publish(f"oscillation/{status_id}", "set")        
            last_status[status_id]["oscillating"] = True
        last_status[status_id]["value"] = payload
        last_status[status_id]["timestamp"] = time.time()
    else:
      last_status[status_id] = {
        "timestamp": time.time(),
        "value": payload,
        "counter": 0,
        "oscillating": False
      }

def main():

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
  )

  def report(message):
    print(message)
    exit()

  if MQTT_USER == "no_set":
    report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set":
    report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set":
    report("MQTT_HOST env vars no set")

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  logging.info("Starting " + SERVICE)
  while True:
      # Send the heartbeat request and wait
      mqtt_client.publish("heartbeats/system", "are-you-there")
      time.sleep(SLEEP_TIME)

if __name__ == "__main__":
  main()
