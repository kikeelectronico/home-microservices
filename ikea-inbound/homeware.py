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

  def publish(self, id, param, value):    
    response = self.__mqtt_client.publish("device/" + id + "/" + param, value)
    if response.rc == 7:
      self.__mqtt_client.reconnect()
      response = self.__mqtt_client.publish("device/" + id + "/" + param, value)

  # Make a get status request to Homeware API
  def get(self, id, param):
    if self.__token == "no_set" or self.__url == "no_set":
      logging.error("Homeware env vars aren't set")
      return None
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
    if self.__token == "no_set" or self.__url == "no_set":
      logging.error("Homeware env vars aren't set")
      return (False, {})
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
