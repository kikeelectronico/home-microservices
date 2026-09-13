from typing import List
from shared.context import Context


class WaterLeakNotificationMessageHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("param") == "currentSensorStateData" and \
            event.get("value")[0]["name"] == "WaterLeak"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        device = context.getDevice(event.get("device_id"))
        device_name = device["description"]["name"]["name"]

        if event.get("value")[0]["currentSensorState"] == "leak":
            actions.append({
                "type": "notification_message_alert",
                "text": f"Fuga de agua detectada por el sensor {device_name}.",
            })
        else:
            actions.append({
                "type": "notification_message_alert",
                "text": f"El sensor {device_name} ha dejado de detectar la fuga de agua.",
            })

        return actions
