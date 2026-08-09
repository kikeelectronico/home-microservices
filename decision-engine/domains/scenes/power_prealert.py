from typing import List
from shared.context import Context


class PowerPrealertSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "current001" and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("value") >= 100:
            actions.append({
                "type": "device_param_update",
                "device_id": "scene_power_prealert",
                "param": "enable",
                "value": True
            })
        elif event.get("value") < 85 and context.get("scene_power_prealert", "enable"):
            actions.append({
                "type": "device_param_update",
                "device_id": "scene_power_prealert",
                "param": "enable",
                "value": False
            })

        return actions
