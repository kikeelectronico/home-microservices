from typing import List
from shared.context import Context


class BedroomAirTemperatureHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "switch_prepare_home" and \
            event.get("param") == "on" and \
            event.get ("value")) or \
            (event.get("device_id") == "switch_at_home" and \
            event.get("param") == "on") or \
            (event.get("device_id") == "scene_awake" and \
            event.get("param") == "enable" and \
            not event.get("value")))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []

        if event.get("device_id") == "switch_prepare_home":
            if context.get("scene_winter", "enable"):
                actions.append({
                    "type": "device_param_update",
                    "device_id": "thermostat_dormitorio",
                    "param": "thermostatTemperatureSetpoint",
                    "value": 21
                })
                actions.append({
                    "type": "device_param_update",
                    "device_id": "thermostat_dormitorio",
                    "param": "thermostatMode",
                    "value": "heat"
                })

        elif event.get("device_id") == "switch_at_home":
            if event.get("value"):
                if context.get("scene_winter", "enable"):
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "thermostat_dormitorio",
                        "param": "thermostatTemperatureSetpoint",
                        "value": 21
                    })
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "thermostat_dormitorio",
                        "param": "thermostatMode",
                        "value": "heat"
                    })
            else:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "thermostat_dormitorio",
                    "param": "thermostatMode",
                    "value": "off"
                })
        elif event.get("device_id") == "scene_awake":
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_dormitorio",
                "param": "thermostatTemperatureSetpoint",
                "value": 18
            })
            actions.append({
                "type": "device_param_update",
                "device_id": "thermostat_dormitorio",
                "param": "thermostatMode",
                "value": "heat" if context.get("scene_winter", "enable") else "off"
            })

        return actions
