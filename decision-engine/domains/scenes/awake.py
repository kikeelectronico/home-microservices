from typing import List
from shared.context import Context


class AwakeSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "pressure001" and \
            event.get("param") == "occupancy"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if not context.get("scene_awake", "enable"):
            actions.append({
                "type": "device_param_update",
                "device_id": "scene_awake",
                "param": "enable",
                "value": True
            })

        return actions
