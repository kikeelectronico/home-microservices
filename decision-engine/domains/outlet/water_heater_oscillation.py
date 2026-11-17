from typing import List

from shared.context import Context

class WaterHeaterOscillationOutletHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "oscillation" and \
            event.get("device_id") == "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1" and \
            event.get("param") == "on"

    def handle(self, event: dict, context: Context) -> List[dict]:
        actions = []

        if event.get("value") == "set":
            actions.append({
                "type": "device_param_update",
                "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                "param": "oscillating",
                "value": True
            })
        elif event.get("value") == "reset":
            actions.append({
                "type": "device_param_update",
                "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                "param": "oscillating",
                "value": False
            })

        return actions
