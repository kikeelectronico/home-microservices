from typing import List
from shared.context import Context


class BathroomRadiatorOutlethHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_power_alert" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatMode") or \
            (event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatTemperatureAmbient") or \
            (event.get("device_id") == "thermostat_bathroom" and \
            event.get("param") == "thermostatTemperatureSetpoint"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        def shouldHeat(context, thermostat_id, radiator_id, sensor_id = None, rule_14 = False):
            current_thermostat_mode = context.get(thermostat_id, "thermostatMode")
            current_thermostat_temperature_ambient = context.get(thermostat_id, "thermostatTemperatureAmbient")
            current_thermostat_temperature_setpoint = context.get(thermostat_id, "thermostatTemperatureSetpoint")
            current_sensor_open = context.get(sensor_id, "openPercent") == 100 if not sensor_id is None else False
            if (current_thermostat_mode == "heat" and not current_sensor_open) or rule_14:
                desired_set_point = current_thermostat_temperature_setpoint if not rule_14 else 14
                if current_thermostat_temperature_ambient < desired_set_point:
                    return True
                elif current_thermostat_temperature_ambient > desired_set_point:
                    return False
                else:
                    return context.get(radiator_id, "on")
            else:
                return False

        if event.get("device_id") == "scene_power_alert":
            if event.get("value"):
                current_lower_priority_decice_power_status = context.getLowerPriorityDevicePowerStatus("9339195d-75c3-4fc1-aeac-03f8af899e40_1")
                if not current_lower_priority_decice_power_status:
                    if context.get("9339195d-75c3-4fc1-aeac-03f8af899e40_1", "on"):
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "9339195d-75c3-4fc1-aeac-03f8af899e40_1",
                            "param": "on",
                            "value": False
                        })
            else:
                desired_on = shouldHeat(context, "thermostat_bathroom", "9339195d-75c3-4fc1-aeac-03f8af899e40_1")
                if context.get("9339195d-75c3-4fc1-aeac-03f8af899e40_1", "on") != desired_on:
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "9339195d-75c3-4fc1-aeac-03f8af899e40_1",
                        "param": "on",
                        "value": desired_on
                    })
        else:
            desired_on = shouldHeat(context, "thermostat_bathroom", "9339195d-75c3-4fc1-aeac-03f8af899e40_1")
            if context.get("9339195d-75c3-4fc1-aeac-03f8af899e40_1", "on") != desired_on:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "9339195d-75c3-4fc1-aeac-03f8af899e40_1",
                    "param": "on",
                    "value": desired_on
                })

        return actions
