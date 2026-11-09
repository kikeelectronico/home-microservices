from typing import List
from shared.context import Context


class OscillationNotificationVoiceHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "oscillation"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        device = context.getDevice(event.get("device_id"))
        device_name = device["description"]["name"]["name"]

        if event.get("value") == "set":
            actions.append({
                "type": "notification_voice_alert",
                "text": f"Oscilación detectada en {device_name}",
            })
        else:
            actions.append({
                "type": "notification_voice_alert",
                "text": f"Oscilación amortiguada en {device_name}",
            })

        return actions
