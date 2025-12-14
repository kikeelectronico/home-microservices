import json
import requests
import logging

class Homeware:

  __mqtt_client = None
  __url = "localhost"
  __token = "token"

  def __init__(self, mqtt_client, host, token):
    self.__mqtt_client = mqtt_client
    self.__url = host
    self.__token = token

  # Make an execution request to Homeware API
  def execute(self, id, param, value):    
    control_payload = {
      "id": id,
      "param": param,
      "value": value,
      "intent": "execute"
    }
    response = self.__mqtt_client.publish("device/control", json.dumps(control_payload))
    if response.rc == 7:
      self.__mqtt_client.reconnect()
      response = self.__mqtt_client.publish("device/control", json.dumps(control_payload))

  # Make a get status request to Homeware API
  def get(self, id, param):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      logging.error("Homeware env vars aren't set")
    else:
      try:
        if param == "all":
          url = self.__url + "/api/devices/" + id + "/states"
        else:
          url = self.__url + "/api/devices/" + id + "/states/" + param
        headers = {"Authorization": "bearer " + self.__token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
          return response.json()
        else:
          logging.warning("Fail to get Homeware status. Status code: " + str(response.status_code))
          return (False, {})
      except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get Homeware status. Conection error.")
        self._fail_to_update = False

  def getDevices(self):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      logging.error("Homeware env vars aren't set")
    else:
      try:
        url = self.__url + "/api/devices/get/"
        headers = {
            "Authorization": "bearer " + self.__token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
          unorderedDevices = response.json()
          devices = {}
          for device in unorderedDevices:
              devices[device['id']] = device
          return (True, devices)
        else:
          logging.warning("Fail to get Homeware devices. Status code: " + str(response.status_code))
          return (False, {})    
      except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get Homeware devices. Conection error.")
        self._fail_to_update = False