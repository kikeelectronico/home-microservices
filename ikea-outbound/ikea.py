import requests
import logging

import urllib3
urllib3.disable_warnings()

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
      
  # Get devices
  def getDevices(self):
    try:
      url = f"https://{self.__host}:8443/v1/devices"
      headers = {
        "Authorization": f"Bearer {self.__token}"
      }
      response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        return response.json()
      logging.warning("Fail to get devices from Ikea Bridge. Status code: " + str(response.status_code))
      return []
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get devices from Ikea Bridge. Connection error.")
        return []
    
  # Get device
  def getDevice(self, device_id=None):
    if not device_id:
      return {}
    try:
      url = f"https://{self.__host}:8443/v1/devices/{device_id}"
      headers = {
        "Authorization": f"Bearer {self.__token}"
      }
      response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        return response.json()
      logging.warning("Fail to get the device with id " + device_id + " from Ikea Bridge. Status code: " + str(response.status_code))
      return {}
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get the device with id " + device_id + " from Ikea Bridge. Connection error.")
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
      
