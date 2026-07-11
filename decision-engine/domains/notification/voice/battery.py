from typing import List
from shared.context import Context

BATTER_LEVEL_THRESHOLD = 10

class BatteryNotificationVoiceHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("param") == "capacityRemaining" and \
            event.get("value")[0]["rawValue"] <= BATTER_LEVEL_THRESHOLD

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []
        battery_level = event.get("value")[0]["rawValue"]
        device = context.getDevice(event.get("device_id"))

        if device:
            device_name = device["name"]["name"]
            actions.append(
                {
                    "type": "notification_voice_alert",
                    "text": f"La batería de {device_name} está agotándose. Tiene un {battery_level} porciento de carga.",
                }
            )

        return actions
