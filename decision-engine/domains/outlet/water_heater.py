from typing import List
from shared.context import Context
import logging
from shared.power import canAddPowerLoad, isLowerPriorityDeviceOn, isHigherPriorityDeviceOn


WATER_HEATER_POWER = 1400

class WaterHeaterOutlethHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "scene_power_alert" and \
            event.get("param") == "enable") or \
            (event.get("device_id") == "fc553d8b-1f45-4337-84ab-5c80a84e61ff_1" and \
            event.get("param") == "isRunning"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("device_id") == "scene_power_alert":
            logging.info("Water heater handler: power alert detected")
            if event.get("value"):
                logging.info("Water heater handler: power alert true")
                if not isLowerPriorityDeviceOn("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1"):
                    logging.info("Water heater handler: lower priority device is off")
                    if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on"):
                        logging.info("Water heater handler: water heater current status on")
                        actions.append({
                            "type": "device_param_update",
                            "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                            "param": "on",
                            "value": False
                        })
                        logging.info("Water heater handler: turning water heater off")
            else:
                logging.info("Water heater handler: power alert false")
                desired_on = not context.get("fc553d8b-1f45-4337-84ab-5c80a84e61ff_1", "isRunning")
                if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                    if desired_on:
                        if isHigherPriorityDeviceOn("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1"):
                            if canAddPowerLoad(context, WATER_HEATER_POWER):
                                logging.info(f"Water heater handler: change status to {"on" if desired_on else "off"}")
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
            logging.info("Water heater handler: the other machine state change")
            desired_on = not event.get("value")
            if context.get("b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1", "on") != desired_on:
                logging.info(f"Water heater handler: change status to {"on" if desired_on else "off"}")
                actions.append({
                    "type": "device_param_update",
                    "device_id": "b0e9f8e8-e670-4f6f-a697-a45014d08b4b_1",
                    "param": "on",
                    "value": desired_on
                })

        return actions
