import time
from google.cloud import bigquery
import logging

from mqtt import set_mqtt_client
from constants import HEARTBEAT_TOPIC, MQTT_PORT, SLEEP_TIME
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare variables
pending_measurement = None
measurements_count = 0
settings = None
mqtt_client = None
bigquery_client = None



def handle_message(topic, payload):
    global pending_measurement
    now = time.perf_counter()

    if topic == settings.response_test_trigger_topic:
        pending_measurement = now
        return

    if topic == settings.response_test_response_topic:
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
    mqtt_client = set_mqtt_client(
        settings.mqtt_host,
        MQTT_PORT,
        settings.mqtt_user,
        settings.mqtt_pass,
        settings.service_id,
        subscriptions=[settings.response_test_trigger_topic, settings.response_test_response_topic],
        message_handler=handle_message
    )
    bigquery_client = bigquery.Client()

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
