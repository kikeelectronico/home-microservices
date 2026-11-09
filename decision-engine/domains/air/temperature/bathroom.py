from typing import List
from shared.context import Context


class BathroomAirTemperatureHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on" and \
            not event.get("value")) or \
            (event.get("device_id") == "" and \
            event.get("param") == "enable" and \
            not event.get("value")) or \
            (event.get("device_id") == "scene_ducha" and \
            event.get("param") == "enable"))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("device_id") in ["switch_at_home", "scene_awake"]:
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_bathroom",
                "param": "thermostatMode",
                "value": "off"
            })
        elif event.get("device_id") == "scene_ducha":
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_bathroom",
                "param": "thermostatTemperatureSetpoint",
                "value": 25 if event.get("value") else 21
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_bathroom",
                "param": "thermostatMode",
                "value": "heat" if event.get("value") else "off"
            })

        return actions
