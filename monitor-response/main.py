import os
import time
from google.cloud import bigquery
import logging

import paho.mqtt.client as mqtt


# Load env vars
if os.environ.get("MQTT_PASS", "no_set") == "no_set":
    from dotenv import load_dotenv

    load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
RESPONSE_DDBB = os.environ.get("RESPONSE_DDBB", "no_set")
TRIGGER_TOPIC = os.environ.get("RESPONSE_TEST_TRIGGER_TOPIC", "device/ee2fcd12-9b2e-478f-826f-a4a5447d3a27/occupancy")
RESPONSE_TOPIC = os.environ.get("RESPONSE_TEST_RESPONSE_TOPIC", "device/hue_7/on")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "monitor-response" + ENV
SLEEP_TIME = 10
TOPICS = [TRIGGER_TOPIC, RESPONSE_TOPIC]

# Declare variables
pending_measurement = None
measurements_count = 0

# Instantiate objects
mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=SERVICE,
    protocol=mqtt.MQTTv5,
)
bigquery_client = bigquery.Client()

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
    for topic in TOPICS:
        client.subscribe(topic, qos=1)
        logging.info(f"Subscribed to {topic}")


# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    if reason_code != 0:
        logging.warning(f"Unexpected MQTT disconnection (reason={reason_code}). Reconnecting...")
        while True:
            try:
                client.reconnect()
                logging.info("Reconnected to MQTT broker")
                break
            except Exception as exc:
                logging.warning(f"Reconnect failed: {exc}")
                time.sleep(5)

# Do tasks when a message is received
def on_message(client, userdata, msg):
    global pending_measurement
    now = time.perf_counter()

    if msg.topic == TRIGGER_TOPIC:
        pending_measurement = now
        return

    if msg.topic == RESPONSE_TOPIC:
        if pending_measurement is None:
            return

        elapsed = now - pending_measurement
        elapsed_ms = elapsed * 1000
        pending_measurement = None
        ts = int(time.time())
        query_job = bigquery_client.query(
            """
                INSERT INTO {}
                (time, trigger, response, durantion)
                VALUES ({},"{}","{}","{}", "{}");
            """.format(RESPONSE_DDBB, ts, TRIGGER_TOPIC, RESPONSE_TOPIC, elapsed_ms)
        )
        query_job.result()


def main() -> None:
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
    if RESPONSE_DDBB == "no_set": report("RESPONSE_DDBB env vars no set")

    # Declare the callback functions
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    # Connect to the mqtt broker
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
