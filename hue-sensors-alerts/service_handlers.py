def contact(homeware, mqtt_client, service):
  if homeware.get("switch_at_home", "on"):
    return

  if "contact_report" not in service:
    return

  state = service["contact_report"].get("state")
  if state == "no_contact":
    mqtt_client.publish("notificacion/text/alert", "Alerta de contacto")


def motion(homeware, mqtt_client, service):
  if homeware.get("switch_at_home", "on"):
    return

  if "motion" not in service:
    return

  is_motion = service["motion"].get("motion")
  if is_motion:
    mqtt_client.publish("notificacion/text/alert", "Alerta de movimiento")
