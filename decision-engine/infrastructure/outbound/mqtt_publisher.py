from typing import Any, Dict, Tuple
import paho.mqtt.client as mqtt
import json
import logging


def action_to_mqtt_message(action: Dict) -> Tuple[str, str]:
    match action["type"]:
        case "device_param_update":
            topic = "device/control"
            payload = json.dumps({
                "id": action["device_id"],
                "param": action["param"],
                "value": action["value"],
                "intent": "execute"
            })
            return topic, payload
    logging.warning("Invalid action: %r", str(action))
    return None, None

def publish_actions(actions: list[Dict], mqtt_client: mqtt) -> None:
    
    for action in actions:
        topic, payload = action_to_mqtt_message(action)
        if topic is not None:
            mqtt_client.publish(topic, payload)


