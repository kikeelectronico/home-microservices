from typing import List
from shared.context import Context


class HallwayLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "ee2fcd12-9b2e-478f-826f-a4a5447d3a27" and \
            event.get("param") == "occupancy"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions =  [
            {
                "type": "device_param_update",
                "device_id": "hue_7",
                "param": "on",
                "value": event.get("value") == "OCCUPIED"
            }
        ]

        return actions
