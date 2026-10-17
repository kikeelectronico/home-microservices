from typing import List
from shared.context import Context


class BathroomBrightnessLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_dim" and \
            event.get("param") == "enable"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = [
            {
                "type": "device_param_update",
                "device_id": "hue_2",
                "param": "brightness",
                "value": 20 if event.get("value") else 80
            },
            {
                "type": "device_param_update",
                "device_id": "hue_3",
                "param": "brightness",
                "value": 20 if event.get("value") else 80
            }
        ]          

        return actions
