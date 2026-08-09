from typing import List
from shared.context import Context


class ShowerWaitingSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            (event.get("device_id") == "scene_ducha" and \
            event.get("param") == "enable")

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

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

        return actions
