from typing import List
from shared.context import Context


class BathroomLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "06612edc-4b7c-4ef3-9f3c-157b9d482f8c" and \
            event.get("param") == "occupancy") or \
            (event.get("device_id") == "hue_sensor_14" and \
            event.get("param") == "on") or \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy") or \
            (event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on"))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("device_id") == "06612edc-4b7c-4ef3-9f3c-157b9d482f8c":
            occupied = event.get("value") == "OCCUPIED"
            if occupied:
                actions.append({
                    "type": "cancel_task",
                    "task_id": "bathroom_light001"
                })
                actions.append({
                    "type": "cancel_task",
                    "task_id": "bathroom_hue_sensor_2"
                })
                
                if context.get("scene_ducha", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "hue_sensor_14",
                        "param": "on",
                        "value": True
                    })
                else:
                    if context.get("scene_dim", "enable"):
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "hue_sensor_2",
                            "param": "on",
                            "value": True
                        })
                    else:
                        if context.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness") > 20:
                            actions.append({
                                "type": "device_param_update",
                                "device_id": "light001",
                                "param": "on",
                                "value": True
                            })
                        else:
                            actions.append({
                                "type": "device_param_update",
                                "device_id": "hue_sensor_2",
                                "param": "on",
                                "value": True
                            })
            else:
                if not context.get("hue_sensor_14", "on"):
                    actions.append({
                        "type": "schedule_task",
                        "task_id": "bathroom_hue_sensor_2",
                        "delta": 60,
                        "target": {
                            "device_id": "hue_sensor_2",
                            "param": "on",
                            "value": False
                        },
                        "asserts": [
                            {
                                "device_id": "06612edc-4b7c-4ef3-9f3c-157b9d482f8c",
                                "param": "occupancy",
                                "value": "UNOCCUPIED"
                            },
                            {
                                "device_id": "9260ed68-0542-4248-9f23-babfae1db2a1_1",
                                "param": "occupancy",
                                "value": "UNOCCUPIED"
                            }
                        ]
                    })
                    actions.append({
                        "type": "schedule_task",
                        "task_id": "bathroom_light001",
                        "delta": 60,
                        "target": {
                            "device_id": "light001",
                            "param": "on",
                            "value": False
                        },
                        "asserts": [
                            {
                                "device_id": "06612edc-4b7c-4ef3-9f3c-157b9d482f8c",
                                "param": "occupancy",
                                "value": "UNOCCUPIED"
                            },
                            {
                                "device_id": "9260ed68-0542-4248-9f23-babfae1db2a1_1",
                                "param": "occupancy",
                                "value": "UNOCCUPIED"
                            }
                        ]
                    })

        elif event.get("device_id") == "hue_sensor_14":
            if event.get("value"):
                if context.get("scene_dim", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "hue_sensor_2",
                        "param": "on",
                        "value": True
                    })
                else:
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "light001",
                        "param": "on",
                        "value": True
                    })
            else:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_sensor_2",
                    "param": "on",
                    "value": False
                })
                actions.append({
                    "type": "device_param_update",
                    "device_id": "light001",
                    "param": "on",
                    "value": False
                })
        
        elif event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            occupied = event.get("value") == "OCCUPIED"
            if occupied:
                if context.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 0:
                    actions.append({
                        "type": "cancel_task",
                        "task_id": "bathroom_light001"
                    })
                    actions.append({
                        "type": "cancel_task",
                        "task_id": "bathroom_hue_sensor_2"
                    })
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "light001",
                        "param": "on",
                        "value": False
                    })
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "hue_sensor_2",
                        "param": "on",
                        "value": False
                    })

        elif event.get("device_id") == "switch_at_home":
            if not event.get("value"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_sensor_14",
                    "param": "on",
                    "value": False
                })
        
        return actions
