from typing import List
from shared.context import Context


class ShowerSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable" and \
            not event.get("value")) or \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy" and \
            event.get("value")))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("device_id") == "scene_awake":
            actions.append({
                "type": "device_param_update",
                "device_id": "scene_ducha",
                "param": "enable",
                "value": False
            })
        elif event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            if context.get("scene_ducha", "enable"):
                if context.get("scene_shower_initiated", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "scene_ducha",
                        "param": "enable",
                        "value": False
                    })

        return actions
