import time
import logging
import paho.mqtt.client as mqtt

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

def set_mqtt_client(host, port, user, password, client_id):
  # Create mqtt client
  client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=client_id,
    protocol=mqtt.MQTTv5
  ) 
  # Connect to the mqtt broker
  client.on_disconnect = on_disconnect
  client.username_pw_set(user, password)
  client.reconnect_delay_set(min_delay=1, max_delay=60)
  client.connect(host, port, 60, clean_start=False)

  return client