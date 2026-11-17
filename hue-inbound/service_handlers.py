def contact(homeware, service, device_id_service_id):
  if "contact_report" in service:
    device_id = device_id_service_id[service["id"]]
    hue_state = service["contact_report"]["state"]
    homeware.execute(device_id, "openPercent", 0 if hue_state == "contact" else 100)


def motion(homeware, service, device_id_service_id):
  if "motion" in service:
    device_id = device_id_service_id[service["id"]]
    hue_motion = service["motion"]["motion"]
    homeware.execute(device_id, "occupancy", "OCCUPIED" if hue_motion else "UNOCCUPIED")


def connectivity(homeware, service, device_id_service_id):
  if "status" in service:
    hue_status = service["status"]

    # Pending on transitioning to v2 IDs for deleting id_v1
    if "id_v1" in service:
      device_id = "hue_" + service["id_v1"].split("/")[2]
      homeware.execute(device_id, "online", hue_status == "connected")
      device_id = "hue_sensor_" + service["id_v1"].split("/")[2]
      homeware.execute(device_id, "online", hue_status == "connected")
    # end of id_v1

    device_id = device_id_service_id[service["id"]]
    homeware.execute(device_id, "online", hue_status == "connected")


def power(homeware, service, device_id_service_id):
  if "power_state" in service:
    hue_battery_level = service["power_state"]["battery_level"]

    # Pending on transitioning to v2 IDs for deleting id_v1
    if "id_v1" in service:
      device_id = "hue_sensor_" + service["id_v1"].split("/")[2]
      if hue_battery_level == 100:
        descriptive_capacity_remaining = "FULL"
      elif hue_battery_level >= 70:
        descriptive_capacity_remaining = "HIGH"
      elif hue_battery_level >= 40:
        descriptive_capacity_remaining = "MEDIUM"
      elif hue_battery_level >= 10:
        descriptive_capacity_remaining = "LOW"
      else:
        descriptive_capacity_remaining = "CRITICALLY_LOW"
      homeware.execute(device_id, "descriptiveCapacityRemaining", descriptive_capacity_remaining)
      homeware.execute(
        device_id,
        "capacityRemaining",
        [{"rawValue": hue_battery_level, "unit": "PERCENTAGE"}]
      )
    # end of id_v1

    device_id = device_id_service_id[service["id"]]
    if hue_battery_level == 100:
      descriptive_capacity_remaining = "FULL"
    elif hue_battery_level >= 70:
      descriptive_capacity_remaining = "HIGH"
    elif hue_battery_level >= 40:
      descriptive_capacity_remaining = "MEDIUM"
    elif hue_battery_level >= 10:
      descriptive_capacity_remaining = "LOW"
    else:
      descriptive_capacity_remaining = "CRITICALLY_LOW"
    homeware.execute(device_id, "descriptiveCapacityRemaining", descriptive_capacity_remaining)
    homeware.execute(
      device_id,
      "capacityRemaining",
      [{"rawValue": hue_battery_level, "unit": "PERCENTAGE"}]
    )


def lightlevel(homeware, service, device_id_service_id):
  if "light" in service:
    hue_brightness = round(service["light"]["light_level"] * 100 / 44000)
    homeware.execute(device_id_service_id[service["id"]], "brightness", hue_brightness)


def light(homeware, service, device_id_service_id):
  if "id_v1" in service:
    device_id = "hue_" + service["id_v1"].split("/")[2]
    if "on" in service:
      hue_on = service["on"]["on"]
      if hue_on != homeware.get(device_id, "on"):
        homeware.execute(device_id, "on", hue_on)
    if "dimming" in service:
      hue_brightness = round(service["dimming"]["brightness"])
      if hue_brightness != homeware.get(device_id, "brightness"):
        homeware.execute(device_id, "brightness", hue_brightness)
    if "color_temperature" in service:
      hue_mirek = service["color_temperature"]["mirek"]
      hue_color_temperature = round(1000000 / hue_mirek)
      homeware_color = homeware.get(device_id, "color")
      homeware_color_temperature = homeware_color.get("temperatureK")
      if homeware_color_temperature and hue_color_temperature != homeware_color_temperature:
        homeware.execute(device_id, "color", {"temperatureK": hue_color_temperature})
