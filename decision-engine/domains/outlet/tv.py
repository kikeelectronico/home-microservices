from typing import List
from shared.context import Context


class TvOutlethHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable"
    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        actions.append({
            "type": "device_param_update",
            "device_id": "hue_12",
            "param": "on",
            "value": event.get("value")
        })

        return actions
