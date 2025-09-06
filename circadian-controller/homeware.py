import json
import requests

class Homeware:

  __mqtt_client = None
  __url = "localhost"
  __token = "token"

  def __init__(self, mqtt_client, host, token, logger):
    self.__mqtt_client = mqtt_client
    self.__url = host
    self.__token = token
    self.logger = logger

  # Make an execution request to Homeware API
  def execute(self, id, param, value):    
    control_payload = {
      "id": id,
      "param": param,
      "value": value,
      "intent": "execute"
    }
    self.__mqtt_client.publish("device/control", json.dumps(control_payload))

  # Make a get status request to Homeware API
  def get(self, id, param):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      self.logger.log("Homeware env vars aren't set", severity="ERROR")
    else:
      try:
        url = self.__url + "/api/devices/" + id + "/states/" + param
        headers = {"Authorization": "bearer " + self.__token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
          return response.json()
        else:
          self.logger.log("Fail to get Homeware status. Status code: " + str(response.status_code), severity="WARNING")
          return (False, {})
      except (requests.ConnectionError, requests.Timeout) as exception:
        self.logger.log("Fail to get Homeware status. Conection error.", severity="WARNING")
        self._fail_to_update = False