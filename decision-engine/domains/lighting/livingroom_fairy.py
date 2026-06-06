from typing import List
from shared.context import Context


class LivingroomFairyLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []
        
        # MAX_LIVINGROOM_LIGHT_BRIGHTNESS = 100
        # MAX_LIVINGROOM_FAIRY_LIGHTS_BRIGHTNESS = 100

        # new_fairy_brightness = (event.get("value") * MAX_LIVINGROOM_FAIRY_LIGHTS_BRIGHTNESS)/MAX_LIVINGROOM_LIGHT_BRIGHTNESS
        # new_fairy_brightness = round(new_fairy_brightness)
        new_fairy_brightness = event.get("value")
        
        if new_fairy_brightness < 10: new_fairy_brightness = 10
        
        if not context.get("rgb001", "brightness") == new_fairy_brightness:
            actions =  [
                {
                    "type": "device_param_update",
                    "device_id": "rgb001",
                    "param": "brightness",
                    "value": new_fairy_brightness
                }
            ]

        return actions
