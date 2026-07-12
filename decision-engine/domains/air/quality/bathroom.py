from typing import List
from shared.context import Context

HUMIDITY_TRIGGER_OFFSET = 5

class BathroomAirQualityHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            (( event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatHumidityAmbient" ) or \
            ( event.get("device_id") == "switch_hood" and \
            event.get("param") == "on" ) or \
            ( event.get("device_id") == "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4" and \
            event.get("param") == "openPercent" ))

    def handle(self, event: dict, context: Context) -> List[dict]:
        
        actions = []
        
        new_hood_state = False
        if context.get("switch_hood", "on"):
            new_hood_state = True
        elif context.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4","openPercent") == 100:
            new_hood_state = True
        else:
            bathroom_humidity = context.get("thermostat_bathroom", "thermostatHumidityAmbient")
            bedroom_humidity = context.get("thermostat_dormitorio", "thermostatHumidityAmbient")
            new_hood_state = bathroom_humidity > bedroom_humidity + HUMIDITY_TRIGGER_OFFSET

        if context.get("hood001", "on") != new_hood_state:
            actions.append({
                "type": "device_param_update",
                "device_id": "hood001",
                "param": "on",
                "value": new_hood_state
            })

        return actions
