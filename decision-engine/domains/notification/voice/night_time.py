from typing import List
from shared.context import Context


class NightTimeVoiceNotificationHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable" and \
            not event.get("value")

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if context.get("e6c2e2bd-5057-49bc-821f-a4b10e415ac6", "openPercent") == 100:
            actions.append(
                {
                    "type": "notification_voice_alert",
                    "text": "La ventana del dormitorio está abierta.",
                }
            )

        if context.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 100:
            actions.append(
                {
                    "type": "notification_voice_alert",
                    "text": "La ventana del salón está abierta.",
                }
            )

        return actions
