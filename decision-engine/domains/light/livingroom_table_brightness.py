from typing import List
from shared.context import Context

MAX_LIVINGROOM_LIGHT_BRIGHTNESS = 100
MAX_LIVINGROOM_TABLE_LIGHT_BRIGHTNESS = 30

class LivingroomTableBrightnessLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" or \
             event.get("device_id") == "hue_11") and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            new_table_brightness = (event.get("value") * MAX_LIVINGROOM_TABLE_LIGHT_BRIGHTNESS)/MAX_LIVINGROOM_LIGHT_BRIGHTNESS
            new_table_brightness = round(new_table_brightness)
            
            if not context.get("hue_11", "brightness") == new_table_brightness:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_11",
                    "param": "brightness",
                    "value": new_table_brightness
                })
        elif event.get("device_id") == "hue_11":
            if event.get("value") > MAX_LIVINGROOM_TABLE_LIGHT_BRIGHTNESS:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_11",
                    "param": "brightness",
                    "value": MAX_LIVINGROOM_TABLE_LIGHT_BRIGHTNESS
                })

        return actions
