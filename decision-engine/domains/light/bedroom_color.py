from typing import List
from shared.context import Context


class BedroomColorLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_power_alert" and \
            event.get("param") == "enable"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
       
        actions.append({
            "type": "device_param_update",
            "device_id": "rgb003",
            "param": "currentToggleSettings",
            "value": {
                "emergencia": event.get("value")
            }
        })

        return actions
