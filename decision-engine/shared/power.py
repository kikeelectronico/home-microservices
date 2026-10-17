import logging
from shared.context import Context
from shared.constants import HOME_POWER_LIMIT, HOME_POWER_MULTIPLIER, ON_POWER_THRESHOLD, POWER_PRIORITY

def canAddPowerLoad (context: Context, required_power):
    current_home_power = context.get("current001", "brightness") * HOME_POWER_MULTIPLIER
    return (HOME_POWER_LIMIT - current_home_power) > required_power

def isLowerPriorityDeviceOn(context: Context, id: str) -> bool:
    if not id in POWER_PRIORITY:
        return False

    device_index = POWER_PRIORITY.index(id)

    if device_index + 1 >= len(POWER_PRIORITY):
        return False
    else:
        lower_priority_device_id = POWER_PRIORITY[device_index+1]
        lower_priority_device_power = context.get(lower_priority_device_id, "power")
        if lower_priority_device_power is None:
            logging.warning(f"Fail to get lower_priority_device_power from lower_priority_device_id {lower_priority_device_id} for device {id} ")
            return False
        return lower_priority_device_power > ON_POWER_THRESHOLD

def isHigherPriorityDeviceOn(context: Context, id: str) -> bool:
    if not id in POWER_PRIORITY:
        return False

    device_index = POWER_PRIORITY.index(id)

    if device_index - 1 < 0:
        return False
    else:
        highest_priority_device_id = POWER_PRIORITY[device_index-1]
        highest_priority_device_power = context.get(highest_priority_device_id, "power")
        if highest_priority_device_power is None:
            logging.warning(f"Fail to get highest_priority_device_power from lower_priority_device_id {highest_priority_device_id} for device {id} ")
            return False
        return highest_priority_device_power > ON_POWER_THRESHOLD