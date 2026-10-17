from typing import List
from shared.context import Context


class SensorsSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "ee2fcd12-9b2e-478f-826f-a4a5447d3a27" and \
            event.get("param") == "occupancy" and \
            event.get("value") == "OCCUPIED") or \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy" and \
            event.get("value") == "OCCUPIED") or \
            (event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("param") == "occupancy":
            if not context.get("scene_sensors_enable", "enable"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "scene_sensors_enable",
                    "param": "enable",
                    "value": True
                })
        elif event.get("device_id") == "scene_awake":
            actions.append({
                "type": "device_param_update",
                "device_id": "scene_sensors_enable",
                "param": "enable",
                "value": event.get("value")
            })

        return actions
