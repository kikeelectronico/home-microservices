from typing import List
from shared.context import Context


class PrepareHomeSwitchHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on" and \
            event.get("value")

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        actions.append({
            "type": "device_param_update",
            "device_id": "switch_prepare_home",
            "param": "on",
            "value": False
        })

        return actions
