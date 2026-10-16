import logging

from mqtt import set_mqtt_client
from engine.engine import Engine
from engine.registry import build_handlers
from infrastructure.inbound.mqtt_parser import mqtt_to_event
from infrastructure.inbound.mqtt_config import TOPICS
from infrastructure.outbound.mqtt_publisher import publish_actions
from settings import Settings
from shared.context import Context
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

settings = None
mqtt_client = None


def handle_message(topic, payload):

    event = mqtt_to_event(topic, payload.decode("utf-8"))
    if event is not None:
        context = Context(mqtt_client, settings.homeware_api_url, settings.homeware_api_key)
        engine = Engine(handlers=build_handlers())
        actions = engine.handle(event, context)

        publish_actions(actions, mqtt_client)
		

def main() -> None:
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
    mqtt_client = set_mqtt_client(
        settings.mqtt_host,
        settings.mqtt_port,
        settings.mqtt_user,
        settings.mqtt_pass,
        settings.service_id,
        subscriptions=TOPICS,
        message_handler=handle_message
    )
    # Main loop
    mqtt_client.loop_start()
    while not stop_requested():
        wait_for_stop(1)

    logging.info("Disconnecting from the MQTT broker.")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    logging.info("Shutdown completed.")


if __name__ == "__main__":
    main()
