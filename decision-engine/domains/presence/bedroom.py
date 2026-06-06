from typing import List
from shared.context import Context


class BedroomPresenceHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "c2b38173-883e-4766-bcb5-0cce2dc0e00e" and \
            event.get("value")

    def handle(self, event: dict, context: Context) -> List[dict]:
        if context.get("pressure002","occupancy") == "UNOCCUPIED":
            return [
                {
                    "type": "device_param_update",
                    "device_id": "c2b38173-883e-4766-bcb5-0cce2dc0e00e",
                    "param": "currentToggleSettings",
                    "value": {"last_seen": True}
                },
                {
                    "type": "device_param_update",
                    "device_id": "06612edc-4b7c-4ef3-9f3c-157b9d482f8c",
                    "param": "currentToggleSettings",
                    "value": {"last_seen": False}
                },
                {
                    "type": "device_param_update",
                    "device_id": "c8bd20a2-69a5-4946-b6d6-3423b560ffa9",
                    "param": "currentToggleSettings",
                    "value": {"last_seen": False}
                }
            ]
