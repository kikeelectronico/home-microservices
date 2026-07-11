
# Alert about living temperature

TEMPERATURE_THRESHOLD = 20
abnormal_livingroom_temperature_alert = False
temperature_reference = 100

def abnormalLivingroomTemperature(homeware, alert, topic, payload):
  global abnormal_livingroom_temperature_alert
  global temperature_reference
  if topic == "device/thermostat_livingroom":
    # Low temperature
    if payload["thermostatTemperatureAmbient"] < TEMPERATURE_THRESHOLD:
      if homeware.get("scene_winter", "enable"):
        if homeware.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 100:
          abnormal_livingroom_temperature_alert = True
          alert.voice("La temperatura está disminuyento demasiado y la ventana del salón está abierta.")
    # High temperature
    if payload["thermostatTemperatureAmbient"] > temperature_reference:
      if homeware.get("scene_summer", "enable"):
        if homeware.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 100:
          abnormal_livingroom_temperature_alert = True
          alert.voice("La temperatura está aumentando y la ventana del salón está abierta.",)
      temperature_reference = payload["thermostatTemperatureAmbient"]
    if payload["thermostatTemperatureAmbient"] < temperature_reference:
      if homeware.get("scene_summer", "enable"):
        if homeware.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 0:
          temperature_reference = payload["thermostatTemperatureAmbient"]
      

  if "device/e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4/openPercent":
    # Thanks for closing the window
    if homeware.get("e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4", "openPercent") == 0 and abnormal_livingroom_temperature_alert:
      abnormal_livingroom_temperature_alert = False
      alert.voice("Gracias por cerrar la ventana.")
    


      

