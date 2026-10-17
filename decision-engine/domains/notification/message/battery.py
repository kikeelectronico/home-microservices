from typing import List
from shared.context import Context

BATTER_LEVEL_THRESHOLD = 10

class BatteryNotificationMessageHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("param") == "capacityRemaining"

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        value = event.get("value")
        if isinstance(value, list):
            if len(value) > 0:
                if isinstance(value[0].get("rawValue"), int):
                    if value[0]["rawValue"] <= BATTER_LEVEL_THRESHOLD:
                        battery_level = event.get("value")[0]["rawValue"]
                        device = context.getDevice(event.get("device_id"))

                        if device:
                            device_name = device["description"]["name"]["name"]
                            actions.append(
                                {
                                    "type": "notification_message_alert",
                                    "text": f"La batería de {device_name} está agotándose. Tiene un {battery_level} porciento de carga.",
                                }
                            )
                        else:
                            actions.append(
                                {
                                    "type": "notification_message_alert",
                                    "text": f"La batería de un dispositivo está agotándose. Tiene un {battery_level} porciento de carga.",
                                }
                            )

        return actions
