from typing import List
from shared.context import Context

LIVINGROOM_TABLE_LIGHT_TEMP_COLOR = 2200

class LivingroomTableColorLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "hue_11" and \
            event.get("param") == "color"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("value") != LIVINGROOM_TABLE_LIGHT_TEMP_COLOR:
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_11",
                "param": "color",
                "value": { "temperatureK": LIVINGROOM_TABLE_LIGHT_TEMP_COLOR }
            })

        return actions
