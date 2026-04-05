import requests
import logging
import json

import urllib3
urllib3.disable_warnings()

class Hue:
  
  __url = "localhost"
  __token = "token"

  def __init__(self, url, token):
    self.__url = url
    self.__token = token

    fail = False
    if self.__url == "no_set":
      logging.error("HUE_HOST env var isn't set")
      fail = True
    if self.__token == "no_set":
      logging.error("HUE_TOKEN env var isn't set")
      fail = True
    if fail:
      exit()
      
  # Get resource
  def getResource(self, resource="device"):
    try:
      url = "https://" + self.__url + "/clip/v2/resource/" + resource
      headers = {
        'hue-application-key': self.__token
      }
      response = requests.get(url, headers=headers, verify=False)
      if response.status_code == 200:
        return response.json()["data"]
      else:
        logging.warning("Fail to get Hue Bridge " + resource + ". Status code: " + str(response.status_code))
        return {}
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get Hue Bridge " + resource + ". Conection error.")
        self._fail_to_update = False
        return {}
    
  # Set light resource
  def updateLightResource(self, hue_id, hue_status):
    try:
      url = "https://" + self.__url + "/clip/v2/resource/light/" + hue_id
      headers = {
        "Content-Type": "application/json",
        "hue-application-key": self.__token
      }
      response = requests.put(url, data = json.dumps(hue_status), headers = headers, verify=False)
      if not response.status_code == 200:
        logging.warning("Fail to update the light " + hue_id + " to Hue Bridge. Status code: " + str(response.status_code))
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to update Hue Bridge lights. Conection error.")
