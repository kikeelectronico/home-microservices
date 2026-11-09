import logging
import paho.mqtt.client as mqtt

from shutdown import stop_requested, wait_for_stop

# Connect to the broker and subscribe to service topics
def on_connect(client, userdata, flags, reason_code, properties):
  logging.info("Connected to MQTT broker (rc=%s)", reason_code)
  for topic in userdata.get("subscriptions", []):
    client.subscribe(topic, qos=1)
    logging.info("Subscribed to MQTT topic %s", topic)

# Forward messages to the service handler
def on_message(client, userdata, message):
  message_handler = userdata.get("message_handler")
  if message_handler is not None:
    message_handler(message.topic, message.payload)

# Reconnect if MQTT disconnects unexpectedly
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

def set_mqtt_client(host, port, user, password, client_id, subscriptions=None, message_handler=None):
  # Create mqtt client
  client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=client_id,
    protocol=mqtt.MQTTv5
  )
  # Connect to the mqtt broker
  client.user_data_set({
    "subscriptions": subscriptions if subscriptions is not None else [],
    "message_handler": message_handler
  })
  client.on_connect = on_connect
  client.on_message = on_message
  client.on_disconnect = on_disconnect
  client.username_pw_set(user, password)
  client.reconnect_delay_set(min_delay=1, max_delay=60)
  client.connect(host, port, 60, clean_start=False)

  return client
