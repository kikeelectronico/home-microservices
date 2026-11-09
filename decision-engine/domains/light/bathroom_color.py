from typing import List
from shared.context import Context


class BathroomColorLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_dim" and \
            event.get("param") == "enable"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = [
            {
                "type": "device_param_update",
                "device_id": "hue_2",
                "param": "color",
                "value": {"temperatureK": 3000 if event.get("value") else 5000}
            },
            {
                "type": "device_param_update",
                "device_id": "hue_3",
                "param": "color",
                "value": {"temperatureK": 3000 if event.get("value") else 5000}
            }
        ]          

        return actions
