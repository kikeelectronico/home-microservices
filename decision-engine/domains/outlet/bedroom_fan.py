from typing import List
from shared.context import Context


class BedroomFanHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c2b38173-883e-4766-bcb5-0cce2dc0e00e" and \
            event.get("param") == "occupancy"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("value") == "OCCUPIED":
            actions.append({
                "type": "cancel_task",
                "task_id": "bedroom_fan"
            })
        else:
            if not context.get("hue_sensor_12", "on"):
                actions.append({
                    "type": "schedule_task",
                    "task_id": "bedroom_fan",
                    "delta": 60,
                    "target": {
                        "device_id": "hue_8",
                        "param": "on",
                        "value": False
                    },
                    "asserts": [
                        {
                            "device_id": "c2b38173-883e-4766-bcb5-0cce2dc0e00e",
                            "param": "currentToggleSettings",
                            "value": {
                                "last_seen": False
                            }
                        },
                        {
                            "device_id": "scene_summer",
                            "param": "enable",
                            "value": True
                        },
                        {
                            "device_id": "hue_8",
                            "param": "on",
                            "value": True
                        }
                    ]
                })
        
        return actions
