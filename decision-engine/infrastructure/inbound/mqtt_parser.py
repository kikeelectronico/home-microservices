from typing import Any, Dict
import json
import logging

def payload_parser(payload: str):
    try:
        if "true" == payload.lower():
            return True
        elif "false" == payload.lower():
            return False
        elif "{" in payload:
            return json.loads(payload)
        else:
            return payload
    except:
        logging.warning("Invalid MQTT payload: %r", payload)
        return None

def mqtt_to_event(topic: str, payload: str) -> Dict[str, Any]:
    if "device" in topic:
        _, device_id, param = topic.split("/")
        value = payload_parser(payload)

        if value is not None:
            return {
                "type": "device_param_update",
                "device_id": device_id,
                "param": param,
                "value": value
            }

    return None
