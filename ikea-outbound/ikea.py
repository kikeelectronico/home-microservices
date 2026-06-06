import requests
import logging

REQUEST_TIMEOUT = 10

class Ikea:
  
  __host = "localhost"
  __token = "token"

  def __init__(self, host, token):
    self.__host = host
    self.__token = token

    fail = False
    if self.__host == "no_set":
      logging.error("IKEA_HOST env var isn't set")
      fail = True
    if self.__token == "no_set":
      logging.error("IKEA_TOKEN env var isn't set")
      fail = True
    if fail:
      exit()
      
  # Get device
  def getDevices(self, device_id="all"):
    try:
      headers = {
        "Authorization": f"Bearer {self.__token}"
      }
      url = f"https://{self.__host}:8443/v1/devices"
      if device_id != "all":
        url = f"{url}/{device_id}"
      response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      response.raise_for_status()
      devices = response.json()
      return devices
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get the IKEA device %s. Connection error.", device_id)
        if device_id == "all": return []
        return {}
      
  # Update device
  def updateDeviceAttribute(self, device_id="all", attribute="isOn", value=False):
    try:
      headers = {
        "Authorization": f"Bearer {self.__token}"
      }
      url = f"https://{self.__host}:8443/v1/devices/{device_id}"
      payload = [{"attributes": {}}]
      payload[0]["attributes"][attribute] = value
      response = requests.patch(url, json=payload, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      response.raise_for_status()
      return response.status_code == 202
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to update the IKEA device %s. Connection error.", device_id)
        return False
      
