from typing import List
from shared.context import Context


class BathroomAirTemperatureHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on" and \
            not event.get("value")) or \
            (event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable" and \
            not event.get("value")))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        actions.append({
            "type": "device_param_update",
            "device_id": "thermostat_bathroom",
            "param": "thermostatMode",
            "value": "off"
        })

        return actions
