from typing import List
from shared.context import Context


class ShowerVoiceNotificationHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_ducha" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatTemperatureAmbient"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("device_id") == "scene_ducha":
            if event.get("value"):
                actions.append({
                    "type": "notification_voice_alert",
                    "text": "Vale, preparo el baño.",
                })
            else:
                actions.append({
                    "type": "notification_voice_alert",
                    "text": "Genial. Dejo de priorizar el baño.",
                })
        elif event.get("device_id") == "thermostat_bathroom":
            if context.get("scene_winter", "enable") and context.get("scene_shower_waiting", "enable"):
                if event.get("value") >= context.get("thermostat_bathroom", "thermostatTemperatureSetpoint"):
                    if not context.get("scene_shower_informed", "enable") and not context.get("scene_shower_initiated", "enable"):
                        actions.append({
                            "type": "notification_voice_alert",
                            "text": "El baño está listo.",
                        })

        return actions
