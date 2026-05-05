from typing import List
from shared.context import Context


class ButtonLightingHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "interruptor_prueba"

    def handle(self, event: dict, context: Context) -> List[dict]:        
        return [
            {
                "type": "device_param_update",
                "device_id": "bombilla_prueba",
                "param": "on",
                "value": event.get("value")
            }
        ]
