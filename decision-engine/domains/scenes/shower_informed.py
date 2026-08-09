from typing import List
from shared.context import Context


class ShowerInformedSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_ducha" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatTemperatureAmbient") or \
            (event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "occupancy" and \
            event.get("value")))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions = []

        if event.get("device_id") == "scene_ducha":
            if not event.get("value"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "scene_shower_informed",
                    "param": "enable",
                    "value": False
                })
        elif event.get("device_id") == "thermostat_bathroom":
            if context.get("scene_winter", "enable") and context.get("scene_shower_waiting", "enable"):
                if event.get("value") >= context.get("thermostat_bathroom", "thermostatTemperatureSetpoint"):
                    if not context.get("scene_shower_informed", "enable") and not context.get("scene_shower_initiated", "enable"):
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "scene_shower_informed",
                            "param": "enable",
                            "value": True
                        })
        elif event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            if context.get("scene_ducha", "enable"):
                if context.get("scene_shower_initiated", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "scene_shower_informed",
                        "param": "enable",
                        "value": False
                    })

        return actions
