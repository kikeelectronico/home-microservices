import logging


def air_purifier(ikea, ikea_id, state):
  current_mode_settings = state.get("currentModeSettings")
  if not isinstance(current_mode_settings, dict):
    logging.warning(
      "Invalid 'currentModeSettings' value for IKEA device %s: %r",
      ikea_id,
      current_mode_settings
    )
    return

  mode = current_mode_settings.get("Modo")
  if not mode:
    logging.warning(
      "Missing 'currentModeSettings.Modo' for IKEA device %s: %r",
      ikea_id,
      current_mode_settings
    )
    return

  fan_speed = state.get("currentFanSpeedSetting")
  match mode:
    case "Apagado":
      ikea.updateDeviceAttribute(ikea_id, "fanMode", "off")
    case "Automático":
      ikea.updateDeviceAttribute(ikea_id, "fanMode", "auto")
    case "Manual":
      ikea.updateDeviceAttribute(ikea_id, "fanMode", "on")
      match fan_speed:
        case "Baja":
          ikea.updateDeviceAttribute(ikea_id, "motorState", 10)
        case "Media":
          ikea.updateDeviceAttribute(ikea_id, "motorState", 30)
        case "Alta":
          ikea.updateDeviceAttribute(ikea_id, "motorState", 50)
      ikea.updateDeviceAttribute(ikea_id, "fanMode", "on")


def on(ikea, ikea_id, state):
  is_on = state.get("on")
  if not isinstance(is_on, bool):
    logging.warning("Invalid 'on' value for IKEA device %s: %r", ikea_id, is_on)
    return

  ikea.updateDeviceAttribute(ikea_id, "isOn", is_on)
