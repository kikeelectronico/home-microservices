import requests
import logging

def contact(host, token, homeware, device_id_service_id):
  url = "https://" + host + "/clip/v2/resource/contact"
  headers = {
    'hue-application-key': token
  }
  response = requests.request("GET", url, headers=headers, verify=False)
  if not response.status_code == 200:
    logging.warning("Unable to load initial values for contact")
  else:
    services = response.json()["data"]
    for service in services:
      homeware.execute(device_id_service_id[service["id"]], "openPercent", 0 if service["contact_report"]["state"] == "contact" else 100)

def motion(host, token, homeware, device_id_service_id):
  url = "https://" + host + "/clip/v2/resource/motion"
  headers = {
    'hue-application-key': token
  }
  response = requests.request("GET", url, headers=headers, verify=False)
  if not response.status_code == 200:
    logging.warning("Unable to load initial values for motion")
  else:
    services = response.json()["data"]
    for service in services:
      homeware.execute(device_id_service_id[service["id"]], "occupancy", "OCCUPIED" if service["motion"]["motion"] else "UNOCCUPIED")

def connectivity(host, token, homeware, device_id_service_id):
  url = "https://" + host + "/clip/v2/resource/zigbee_connectivity"
  headers = {
    'hue-application-key': token
  }
  response = requests.request("GET", url, headers=headers, verify=False)
  if not response.status_code == 200:
    logging.warning("Unable to load initial values for zigbee_connectivity")
  else:
    services = response.json()["data"]
    for service in services:
      if "id_v1" in service:
        id_v1_splited = service["id_v1"].split("/")
        device_id = "hue_" + ("sensor_" if id_v1_splited[1] == "sensors" else "") + id_v1_splited[2]
        homeware.execute(device_id, "online", True if service["status"] == "connected" else False)
      homeware.execute(device_id_service_id[service["id"]], "online", True if service["status"] == "connected" else False)

def power(host, token, homeware, device_id_service_id):
  url = "https://" + host + "/clip/v2/resource/device_power"
  headers = {
    'hue-application-key': token
  }
  response = requests.request("GET", url, headers=headers, verify=False)
  if not response.status_code == 200:
    logging.warning("Unable to load initial values for device_power")
  else:
    services = response.json()["data"]
    for service in services:
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
      device_id = device_id_service_id[service["id"]]
      battery_level = service["power_state"]["battery_level"]
      if battery_level == 100: descriptiveCapacityRemaining = "FULL"
      elif battery_level >= 70: descriptiveCapacityRemaining = "HIGH"
      elif battery_level >= 40: descriptiveCapacityRemaining = "MEDIUM"
      elif battery_level >= 10: descriptiveCapacityRemaining ="LOW"
      else: descriptiveCapacityRemaining = "CRITICALLY_LOW"
      homeware.execute(device_id,"descriptiveCapacityRemaining", descriptiveCapacityRemaining)
      homeware.execute(device_id, "capacityRemaining", [{"rawValue": battery_level, "unit":"PERCENTAGE"}])

def lightlevel(host, token, homeware, device_id_service_id):
  url = "https://" + host + "/clip/v2/resource/light_level"
  headers = {
    'hue-application-key': token
  }
  response = requests.request("GET", url, headers=headers, verify=False)
  if not response.status_code == 200:
    logging.warning("Unable to load initial values for light_level")
  else:
    services = response.json()["data"]
    for service in services:
      brightness = round(service["light"]["light_level"] * 100 / 44000)
      homeware.execute(device_id_service_id[service["id"]], "brightness", brightness)