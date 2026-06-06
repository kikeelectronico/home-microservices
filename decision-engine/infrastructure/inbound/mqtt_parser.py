from typing import Any, Dict
import json
import logging

def payload_parser(payload: str):
    payload = payload.strip()
    try:
       return json.loads(payload)
    except:
        return payload

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
