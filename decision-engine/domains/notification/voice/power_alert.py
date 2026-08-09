from typing import List
from shared.context import Context


class PowerAlertNotificationVoiceHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_power_alert" and \
            event.get("param") == "enable"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("value"):
            actions.append({
                "type": "notification_voice_alert",
                "text": "Sobrecarga de potencia.",
            })
        else:
            actions.append({
                "type": "notification_voice_alert",
                "text": "Sistemas de potencia bajo control.",
            })

        return actions
