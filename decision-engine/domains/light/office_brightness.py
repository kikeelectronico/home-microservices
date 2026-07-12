from typing import List
from shared.context import Context

MIN_LIVINGROOM_DARKNESS_TRIGGER = 15
MIN_WORKTABLE_BRIGHTNESS = 10
WORKTABLE_DYNAMIC_BRIGNTNESS_MULTIPLIER = 1.5

class OfficeBrightnessLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "brightness"

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if context.get("scene_awake", "enable"):
            new_office_brightness = MIN_WORKTABLE_BRIGHTNESS if event.get("value") < MIN_LIVINGROOM_DARKNESS_TRIGGER else int(event.get("value")*WORKTABLE_DYNAMIC_BRIGNTNESS_MULTIPLIER)
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_9",
                "param": "brightness",
                "value": new_office_brightness
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_10",
                "param": "brightness",
                "value": new_office_brightness
            })

        return actions
