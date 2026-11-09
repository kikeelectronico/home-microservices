from typing import List
from shared.context import Context


class KitchenLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy") or \
            (event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on") or \
            (event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable") and \
            event.get("value"))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            occupied = event.get("value") == "OCCUPIED"
            if occupied:
                if not context.get("scene_awake", "enable"):
                    actions.append({
                            "type": "cancel_task",
                            "task_id": "hue_15"
                        })
                    actions.append({
                            "type": "device_param_update",
                            "device_id": "hue_15",
                            "param": "on",
                            "value": True
                        })
            else:
                if not context.get("scene_awake", "enable"):
                    actions.append({
                        "type": "schedule_task",
                        "task_id": "hue_15",
                        "delta": 60,
                        "target": {
                            "device_id": "hue_15",
                            "param": "on",
                            "value": False
                        },
                        "asserts": [
                            {
                                "device_id": "c8bd20a2-69a5-4946-b6d6-3423b560ffa9",
                                "param": "occupancy",
                                "value": "UNOCCUPIED"
                            },
                            {
                                "device_id": "scene_awake",
                                "param": "enable",
                                "value": False
                            },
                            {
                                "device_id": "hue_15",
                                "param": "currentToggleSettings",
                                "value": {
                                    "emergencia": False
                                }
                            }
                        ]
                    })
        elif event.get("device_id") == "switch_at_home":
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_15",
                "param": "on",
                "value": event.get("value")
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_16",
                "param": "on",
                "value": event.get("value")
            })
            if not event.get("value"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "light004",
                    "param": "on",
                    "value": False
                })
        elif event.get("device_id") == "scene_awake":
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_15",
                "param": "on",
                "value": True
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_16",
                "param": "on",
                "value": True
            })

        return actions
