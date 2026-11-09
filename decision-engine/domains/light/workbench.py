from typing import List
from shared.context import Context


class WorkbenchLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "temp_switch" and \
            event.get("param") == "on"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("value"):
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_4",
                "param": "color",
                "value": {"temperatureK": 5000}
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_5",
                "param": "color",
                "value": {"temperatureK": 5000}
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_4",
                "param": "brightness",
                "value": 100
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_5",
                "param": "brightness",
                "value": 100
            })
        actions.append({
            "type": "device_param_update",
            "device_id": "hue_4",
            "param": "on",
            "value": event.get("value")
        })
        actions.append({
            "type": "device_param_update",
            "device_id": "hue_5",
            "param": "on",
            "value": event.get("value")
        })

        return actions
