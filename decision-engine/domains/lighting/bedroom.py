from typing import List
from shared.context import Context


class BedroomLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c2b38173-883e-4766-bcb5-0cce2dc0e00e" and \
            event.get("param") == "occupancy"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
        occupied = event.get("value") == "OCCUPIED"
        if occupied:

            actions.append({
                    "type": "cancel_task",
                    "task_id": "bedroom_rgb003"
                })
            actions.append({
                    "type": "cancel_task",
                    "task_id": "bedroom_hue_6"
                })
            
            if context.get("c2b38173-883e-4766-bcb5-0cce2dc0e00e", "brightness") < 40:
                if context.get("scene_sensors_enable","enable"):
                    if context.get("scene_dim","enable"):
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "rgb003",
                            "param": "on",
                            "value": True
                        })
                    else:
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "hue_6",
                            "param": "on",
                            "value": True
                        })
        else:
            if not context.get("hue_sensor_12", "on"):
                actions.append({
                    "type": "schedule_task",
                    "task_id": "bedroom_hue_6",
                    "delta": 60,
                    "target": {
                        "device_id": "hue_6",
                        "param": "on",
                        "value": False
                    },
                    "asserts": [
                        {
                            "device_id": "c2b38173-883e-4766-bcb5-0cce2dc0e00e",
                            "param": "occupancy",
                            "value": "UNOCCUPIED"
                        }
                    ]
                })
                actions.append({
                    "type": "schedule_task",
                    "task_id": "bedroom_rgb003",
                    "delta": 60,
                    "target": {
                        "device_id": "rgb003",
                        "param": "on",
                        "value": False
                    },
                    "asserts": [
                        {
                            "device_id": "c2b38173-883e-4766-bcb5-0cce2dc0e00e",
                            "param": "occupancy",
                            "value": "UNOCCUPIED"
                        }
                    ]
                })
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
