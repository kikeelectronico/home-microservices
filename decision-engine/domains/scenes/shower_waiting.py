from typing import List
from shared.context import Context


class ShowerWaitingSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_ducha" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy" and \
            event.get("value")))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("device_id") == "scene_ducha":
            if event.get("value"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "scene_shower_waiting",
                    "param": "enable",
                    "value": True
                })
            else:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "scene_shower_waiting",
                    "param": "enable",
                    "value": False
                })
        elif event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            if context.get("scene_ducha", "enable"):
                if context.get("scene_shower_initiated", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "scene_shower_waiting",
                        "param": "enable",
                        "value": False
                    })

        return actions
