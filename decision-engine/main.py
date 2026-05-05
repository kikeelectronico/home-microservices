import paho.mqtt.client as mqtt
import os
import logging
import time

from engine.engine import Engine
from engine.registry import build_handlers
from infrastructure.inbound.mqtt_parser import mqtt_to_event
from infrastructure.inbound.mqtt_config import TOPICS
from infrastructure.outbound.mqtt_publisher import publish_actions
from shared.context import Context


# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "decision-engine-" + ENV

# Instantiate objects
mqtt_client = mqtt.Client(
	mqtt.CallbackAPIVersion.VERSION2,
	client_id=SERVICE,
	protocol=mqtt.MQTTv5
)

# Suscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
	for topic in TOPICS:
		client.subscribe(topic, qos=1)

# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, rc, properties):
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

# Do tasks when a message is received
def on_message(client, userdata, msg):

    event = mqtt_to_event(msg.topic, msg.payload.decode("utf-8"))
    if event is not None:
        context = Context(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)
        engine = Engine(handlers=build_handlers())
        actions = engine.handle(event, context)

        publish_actions(actions, mqtt_client)
		

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-10s %(name)-5s %(message)s"
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
    # Declare the callback functions
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    # Connect to the mqtt broker
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60, clean_start=False)
    logging.info("Starting " + SERVICE)
    # Main loop
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
