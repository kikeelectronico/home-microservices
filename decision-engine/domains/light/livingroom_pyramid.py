from typing import List
from shared.context import Context


class LivingroomPyramidLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "hue_17" and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  [
            {
                "type": "device_param_update",
                "device_id": "hue_17",
                "param": "on",
                "value": True
            }
        ]

        return actions
