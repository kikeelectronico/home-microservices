def contact(service, homeware, device_id_service_id):
  homeware.execute(device_id_service_id[service["id"]], "openPercent", 0 if service["contact_report"]["state"] == "contact" else 100)

def motion(service, homeware, device_id_service_id):
  homeware.execute(device_id_service_id[service["id"]], "occupancy", "OCCUPIED" if service["motion"]["motion"] else "UNOCCUPIED")

def connectivity(service, homeware, device_id_service_id):
  # Pending on transitioning to v2 ids for deleting id_v1
  if "id_v1" in service:
    device_id = "hue_" + service["id_v1"].split("/")[2]
    homeware.execute(device_id, "online", True if service["status"] == "connected" else False)
    device_id = "hue_sensor_" + service["id_v1"].split("/")[2]
    homeware.execute(device_id, "online", True if service["status"] == "connected" else False)
  # end of id_v1
  device_id = device_id_service_id[service["id"]]
  homeware.execute(device_id, "online", True if service["status"] == "connected" else False)

def power(service, homeware, device_id_service_id):
  # Pending on transitioning to v2 ids for deleting id_v1
  if "id_v1" in service:
    device_id = "hue_sensor_" + service["id_v1"].split("/")[2]
    battery_level = service["power_state"]["battery_level"]
    if battery_level == 100: descriptiveCapacityRemaining = "FULL"
    elif battery_level >= 70: descriptiveCapacityRemaining = "HIGH"
    elif battery_level >= 40: descriptiveCapacityRemaining = "MEDIUM"
    elif battery_level >= 10: descriptiveCapacityRemaining ="LOW"
    else: descriptiveCapacityRemaining = "CRITICALLY_LOW"
    homeware.execute(device_id,"descriptiveCapacityRemaining", descriptiveCapacityRemaining)
    homeware.execute(device_id, "capacityRemaining", [{"rawValue": battery_level, "unit":"PERCENTAGE"}])
  # end of id_v1
  device_id = device_id_service_id[service["id"]]
  battery_level = service["power_state"]["battery_level"]
  if battery_level == 100: descriptiveCapacityRemaining = "FULL"
  elif battery_level >= 70: descriptiveCapacityRemaining = "HIGH"
  elif battery_level >= 40: descriptiveCapacityRemaining = "MEDIUM"
  elif battery_level >= 10: descriptiveCapacityRemaining ="LOW"
  else: descriptiveCapacityRemaining = "CRITICALLY_LOW"
  homeware.execute(device_id,"descriptiveCapacityRemaining", descriptiveCapacityRemaining)
  homeware.execute(device_id, "capacityRemaining", [{"rawValue": battery_level, "unit":"PERCENTAGE"}])

def lightlevel(service, homeware, device_id_service_id):
  brightness = round(service["light"]["light_level"] * 100 / 44000)
  homeware.execute(device_id_service_id[service["id"]], "brightness", brightness)

def light(service, homeware, device_id_service_id):
  if "id_v1" in service:
    device_id = "hue_" + service["id_v1"].split("/")[2]
    if "on" in service:
      status = service["on"]["on"]
      if not status == homeware.get(device_id, "on"):
        homeware.execute(device_id,"on", service["on"]["on"])
