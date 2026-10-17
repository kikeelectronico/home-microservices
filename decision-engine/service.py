from engine.engine import Engine
from engine.registry import build_handlers
from infrastructure.inbound.mqtt_parser import mqtt_to_event
from infrastructure.outbound.mqtt_publisher import publish_actions
from shared.context import Context


class DecisionEngineService:

    def __init__(self, settings):
        self.settings = settings
        self.mqtt_client = None

    def initialize(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def _handle_message(self, topic, payload):
        event = mqtt_to_event(topic, payload.decode("utf-8"))
        if event is not None:
            context = Context(
                self.mqtt_client,
                self.settings.homeware_api_url,
                self.settings.homeware_api_key
            )
            engine = Engine(handlers=build_handlers())
            actions = engine.handle(event, context)

            publish_actions(actions, self.mqtt_client)
