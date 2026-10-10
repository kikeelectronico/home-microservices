from shared.context import Context
from shared.constants import HOME_POWER_LIMIT, HOME_POWER_MULTIPLIER

def canAddPowerLoad (context: Context, required_power):
    current_home_power = context.get("current001", "brightness") * HOME_POWER_MULTIPLIER
    return (HOME_POWER_LIMIT - current_home_power) > required_power