from typing import List
from shared.context import Context


class LivingroomAirTemperatureHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "switch_prepare_home" and \
            event.get("param") == "on" and \
            event.get ("value")

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if context.get("scene_winter", "enable"):
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_livingroom",
                "param": "thermostatTemperatureSetpoint",
                "value": 22
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_livingroom",
                "param": "thermostatMode",
                "value": "heat"
            })


        return actions
