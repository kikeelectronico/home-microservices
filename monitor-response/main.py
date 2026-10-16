import time
from google.cloud import bigquery
import logging

import paho.mqtt.client as mqtt
from constants import HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
pending_measurement = None
measurements_count = 0
settings = None
mqtt_client = None
bigquery_client = None

# Subscribe to topics on connect
def on_connect(client, userdata, flags, rc, properties):
    for topic in (settings.response_test_trigger_topic, settings.response_test_response_topic):
        client.subscribe(topic, qos=1)
        logging.info(f"Subscribed to {topic}")


# Reconnect if MQTT disconnects unexpectedly
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    if reason_code != 0:
        logging.warning(f"Unexpected MQTT disconnection (reason={reason_code}). Reconnecting...")
        while not stop_requested():
            try:
                client.reconnect()
                logging.info("Reconnected to MQTT broker")
                break
            except Exception as exc:
                logging.warning(f"Reconnect failed: {exc}")
                wait_for_stop(5)

# Do tasks when a message is received
def on_message(client, userdata, msg):
    global pending_measurement
    now = time.perf_counter()

    if msg.topic == settings.response_test_trigger_topic:
        pending_measurement = now
        return

    if msg.topic == settings.response_test_response_topic:
        if pending_measurement is None:
            return

        elapsed = now - pending_measurement
        elapsed_ms = int(elapsed * 1000)
        pending_measurement = None
        ts = int(time.time())
        query_job = bigquery_client.query(
            """
                INSERT INTO {}
                (time, trigger, response, duration)
                VALUES ({},"{}","{}",{});
            """.format(settings.response_ddbb, ts, settings.response_test_trigger_topic, settings.response_test_response_topic, elapsed_ms)
        )
        query_job.result()


def main() -> None:
    global settings
    global mqtt_client
    global bigquery_client
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
        protocol=mqtt.MQTTv5,
    )
    bigquery_client = bigquery.Client()

    # Declare the callback functions
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    # Connect to the mqtt broker
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
