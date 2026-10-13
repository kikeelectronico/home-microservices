from typing import List
from shared.context import Context
from shared.power import canAddPowerLoad, isLowerPriorityDeviceOn, isHigherPriorityDeviceOn


WATER_HEATER_POWER = 1400

class WaterHeaterOutlethHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_power_prealert" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "fc553d8b-1f45-4337-84ab-5c80a84e61ff_1" and \
            event.get("param") == "isRunning"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("device_id") == "scene_power_prealert":
            if event.get("value"):
                if not isLowerPriorityDeviceOn(context, "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1"):
                    if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on"):
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                            "param": "on",
                            "value": False
                        })
            else:
                desired_on = not context.get("fc553d8b-1f45-4337-84ab-5c80a84e61ff_1", "isRunning")
                if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                    if desired_on:
                        if isHigherPriorityDeviceOn(context, "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1"):
                            if canAddPowerLoad(context, WATER_HEATER_POWER):
                                actions.append({
                                    "type": "device_param_update",
                                    "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                                    "param": "on",
                                    "value": True
                                }) 
                    else:
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                            "param": "on",
                            "value": False
                        }) 
        elif event.get("device_id") == "fc553d8b-1f45-4337-84ab-5c80a84e61ff_1":
            desired_on = not event.get("value")
            if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                    "param": "on",
                    "value": desired_on
                })

        return actions
