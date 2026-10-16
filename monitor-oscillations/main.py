import logging
import time
import paho.mqtt.client as mqtt
from constants import HEARTBEAT_TOPIC, MQTT_PORT, OSCILLATION_THRESHOLD, PARAMS, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None
last_status = {}

def on_connect(client, userdata, flags, rc, properties):
  logging.info("Connected to MQTT broker (rc=%s)", rc)
  client.subscribe(HEARTBEAT_TOPIC, qos=1)
  for topic in PARAMS:
    client.subscribe(f"device/{topic}", qos=1)

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


def on_message(client, userdata, msg):
  global last_status

  if msg.topic == HEARTBEAT_TOPIC:
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
  global settings
  global mqtt_client

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

  mqtt_client.on_message = on_message
  mqtt_client.on_connect = on_connect
  mqtt_client.on_disconnect = on_disconnect
  mqtt_client.username_pw_set(settings.mqtt_user, settings.mqtt_pass)
  mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
  mqtt_client.connect(settings.mqtt_host, MQTT_PORT, 60, clean_start=False)
  mqtt_client.loop_start()
  while not stop_requested():
      # Send the heartbeat request and wait
      mqtt_client.publish(HEARTBEAT_TOPIC, "are-you-there")
      wait_for_stop(SLEEP_TIME)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
