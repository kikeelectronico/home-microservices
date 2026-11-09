from typing import List
from shared.context import Context


class LivingroomPyramidLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "hue_17" and \
            event.get("param") == "brightness") or \
            (event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("device_id") == "hue_17":
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_17",
                "param": "on",
                "value": True
            })
        elif event.get("device_id") == "switch_at_home":
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_17",
                "param": "on",
                "value": event.get("value")
            })

        return actions
