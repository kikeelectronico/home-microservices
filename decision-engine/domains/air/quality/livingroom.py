from typing import List
from shared.context import Context


class LivingroomAirQualityHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            (( event.get("device_id") == "scene_headphones" and \
            event.get("param") == "enable" ) or \
            ( event.get("device_id") == "9260ed68-0542-4248-9f23-babfae1db2a1_1" and \
            event.get("param") == "occupancy" ))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
        
        current_mode_settings = context.get("df31ac85-be3f-48db-ab5e-483001f3ad27_1", "currentModeSettings")

        if current_mode_settings:
            if event.get("device_id") == "scene_headphones":
                if not current_mode_settings.get("Modo") == "Manual" if event.get("value") else "Automático":
                    actions = [
                        {
                            "type": "device_param_update",
                            "device_id": "df31ac85-be3f-48db-ab5e-483001f3ad27_1",
                            "param": "currentModeSettings",
                            "value": {
                                "Modo": "Manual" if event.get("value") else "Automático"
                            }
                        }
                    ]
            else:
                if not current_mode_settings.get("Modo") == "Manual" if event.get("value") == "OCCUPIED" else "Automático":
                    if context.get("scene_ducha", "enable"):
                            actions = [
                            {
                                "type": "device_param_update",
                                "device_id": "df31ac85-be3f-48db-ab5e-483001f3ad27_1",
                                "param": "currentModeSettings",
                                "value": {
                                    "Modo": "Manual" if event.get("value") == "OCCUPIED" else "Automático"
                                }
                            }
                    ]

        return actions
