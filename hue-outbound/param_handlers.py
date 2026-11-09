import logging


def on(hue, hue_service_id, value):
  if not isinstance(value, bool):
    logging.warning("Invalid on value: %r", value)
    return
  hue.updateLightService(hue_service_id, {"on": {"on": value}})


def brightness(hue, hue_service_id, value):
  if not isinstance(value, (int, float)) or not 0 <= value <= 100:
    logging.warning("Invalid brightness value: %r", value)
    return
  hue.updateLightService(hue_service_id, {"dimming": {"brightness": value}})


def color(hue, hue_service_id, value):
  temperature_k = value.get("temperatureK") if isinstance(value, dict) else None
  if not isinstance(temperature_k, (int, float)) or temperature_k <= 0:
    logging.warning("Invalid color temperature: %r", temperature_k)
    return
  hue.updateLightService(
    hue_service_id,
    {"color_temperature": {"mirek": round(1000000 / temperature_k)}}
  )


def emergency(hue, hue_service_id, value):
  if not isinstance(value, bool):
    logging.warning("Invalid emergency setting: %r", value)
    return

  if value:
    hue_service_properties = {
      "on": {"on": True},
      "dimming": {"brightness": 100},
      "effects": {"status": "cosmos"},
      "effects_v2": {
        "action": {
          "effect": "cosmos",
          "parameters": {
            "color": {"xy": {"x": 0.6845, "y": 0.3064}},
            "speed": 0.6151
          }
        }
      },
      "color": {"xy": {"x": 0.6845, "y": 0.3064}}
    }
  else:
    hue_current_service = hue.getService("light", hue_service_id)
    if "effects_v2" not in hue_current_service:
      return

    hue_current_effects_v2_property = hue_current_service["effects_v2"]
    if hue_current_effects_v2_property["status"]["effect"] == "no_effect":
      return

    hue_service_properties = {
      "on": {"on": True},
      "dimming": {"brightness": 22},
      "effects": {"status": "no_effect"},
      "effects_v2": {
        "status": {"effect": "no_effect", "parameters": None}
      },
      "color_temperature": {
        "mirek": round(1000000 / 2200),
        "mirek_valid": True
      }
    }

  hue.updateLightService(hue_service_id, hue_service_properties)
