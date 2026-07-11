from typing import List
from shared.context import Context


class OfficeLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "pressure001" and \
            event.get("param") == "occupancy"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
        occupied = event.get("value") == "OCCUPIED"

        if occupied:
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_9",
                "param": "on",
                "value": False
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_10",
                "param": "on",
                "value": False
            })
            if not context.get("scene_awake", "enable"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "scene_awake",
                    "param": "enable",
                    "value": True
                })

        return actions
