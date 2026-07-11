from typing import List
from shared.context import Context


class HallwayBrightnessLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
       
        if not context.get("scene_dim", "enable"):
            new_hallway_brightness = int((int(event.get("value")) * 1.4) + 20)
            
            if not context.get("hue_7", "brightness") == new_hallway_brightness:
                actions =  [
                    {
                        "type": "device_param_update",
                        "device_id": "hue_7",
                        "param": "brightness",
                        "value": new_hallway_brightness
                    }
                ]

        return actions
