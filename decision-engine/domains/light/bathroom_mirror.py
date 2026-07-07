from typing import List
from shared.context import Context


class BathroomMirrorLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "hue_sensor_2" and \
            event.get("param") == "on"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = [
            {
                "type": "device_param_update",
                "device_id": "hue_2",
                "param": "on",
                "value": event.get("value")
            },
            {
                "type": "device_param_update",
                "device_id": "hue_3",
                "param": "on",
                "value": event.get("value")
            }
        ]          

        return actions
