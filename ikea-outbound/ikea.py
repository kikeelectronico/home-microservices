import requests

class Ikea:
  
  __url = "localhost"
  __token = "token"

  def __init__(self, host, token, logger):
    self.__host = host
    self.__token = token
    self.logger = logger
      
  # Get device
  def getDevices(self, device_id="all"):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      self.logger.log("Hue env vars aren't set", severity="ERROR")
    else:
      try:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.__token}"
        })
        url = f"https://{self.__host}:8443/v1/devices"
        if device_id != "all":
          url = f"{url}/{device_id}"
        response = session.get(url, verify=False)
        response.raise_for_status()
        devices = response.json()
        return devices
      except (requests.ConnectionError, requests.Timeout) as exception:
          self.logger.log("Fail to get Ikea hub " + device_id + ". Conection error.", severity="WARNING")
          self._fail_to_update = False
          if device_id == "all": return []
          return {}
      
  # Update device
  def setDevice(self, device_id="all", attribute="isOn", value=False):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      self.logger.log("Hue env vars aren't set", severity="ERROR")
    else:
      try:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.__token}"
        })
        url = f"https://{self.__host}:8443/v1/devices/{device_id}"
        payload = [{"attributes": {}}]
        payload[0]["attributes"][attribute] = value
        response = session.patch(url, json=payload, verify=False)
        response.raise_for_status()
        return response.status_code == 202
      except (requests.ConnectionError, requests.Timeout) as exception:
          self.logger.log("Fail to get Ikea hub " + device_id + ". Conection error.", severity="WARNING")
          self._fail_to_update = False
          return False
      
