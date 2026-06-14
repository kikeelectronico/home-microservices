import json
import requests
import logging

REQUEST_TIMEOUT = 10

class Homeware:

  __mqtt_client = None
  __url = "localhost"
  __token = "token"

  def __init__(self, mqtt_client, host, token):
    self.__mqtt_client = mqtt_client
    self.__url = host
    self.__token = token

    fail = False
    if self.__url == "no_set":
      logging.error("HOMEWARE_API_URL env var isn't set")
      fail = True
    if self.__token == "no_set":
      logging.error("HOMEWARE_API_KEY env var isn't set")
      fail = True
    if fail:
      exit()

  # Make an execution request to Homeware API
  def execute(self, id, param, value):    
    control_payload = {
      "id": id,
      "param": param,
      "value": value,
      "intent": "execute"
    }
    self.__mqtt_client.publish("device/control", json.dumps(control_payload))

  def publish(self, id, param, value):    
    self.__mqtt_client.publish("device/" + id + "/" + param, value)

  # Make a get status request to Homeware API
  def get(self, id, param):
    try:
      url = self.__url + "/api/devices/" + id + "/states/" + param
      headers = {"Authorization": "bearer " + self.__token}
      response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        return response.json()
      logging.warning("Fail to get Homeware status. Status code: %s", response.status_code)
      return None
    except (requests.ConnectionError, requests.Timeout):
      logging.warning("Fail to get Homeware status. Connection error.")
      return None

  def getDevices(self):
    try:
      url = self.__url + "/api/devices"
      headers = {
          "Authorization": "bearer " + self.__token
      }
      response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        unorderedDevices = response.json()
        devices = {}
        for device in unorderedDevices:
            devices[device['id']] = device
        return (True, devices)
      logging.warning("Fail to get Homeware devices. Status code: %s", response.status_code)
      return (False, {})
    except (requests.ConnectionError, requests.Timeout):
      logging.warning("Fail to get Homeware devices. Connection error.")
      return (False, {})
