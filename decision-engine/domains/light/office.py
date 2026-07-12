from typing import List
from shared.context import Context


class OfficeLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "pressure001" and \
            event.get("param") == "occupancy") or \
            (event.get("device_id") == "0b97c3c8-cb02-4f6d-9e60-d5755b25b968_1" and \
            event.get("param") == "occupancy"))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
        occupied = event.get("value") == "OCCUPIED"

        if event.get("device_id") == "pressure001":
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
        elif event.get("device_id") == "0b97c3c8-cb02-4f6d-9e60-d5755b25b968_1":
            if occupied:
                if context.get("pressure001", "occupancy") == "UNOCCUPIED":
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "hue_9",
                        "param": "on",
                        "value": True
                    })
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "hue_10",
                        "param": "on",
                        "value": True
                    })

        return actions
