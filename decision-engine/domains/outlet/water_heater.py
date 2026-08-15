from typing import List
from shared.context import Context


class WaterHeaterOutlethHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "current001" and \
            event.get("param") == "brightness") or \
            (event.get("device_id") == "fc553d8b-1f45-4337-84ab-5c80a84e61ff_1" and \
            event.get("param") == "isRunning"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []
        desired_on = False

        if not context.get("fc553d8b-1f45-4337-84ab-5c80a84e61ff_1", "isRunning"):
            desired_on = True

        if context.get("scene_power_alert", "enable"):
            current_lower_priority_decice_power_status = context.getLowerPriorityDevicePowerStatus("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1")
            if current_lower_priority_decice_power_status:
                if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                    actions.append({
                        "type": "device_param_update",
                        "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                        "param": "on",
                        "value": desired_on
                    })
            else:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                    "param": "on",
                    "value": False
                })
        else:
            if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                actions.append({
                    "type": "device_param_update",
                    "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                    "param": "on",
                    "value": desired_on
                })

        return actions
