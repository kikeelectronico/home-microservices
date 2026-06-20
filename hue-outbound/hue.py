import requests
import logging
import json

import urllib3
urllib3.disable_warnings()

REQUEST_TIMEOUT = 10

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
      
  # Get services
  def getServices(self, type="device"):
    try:
      url = "https://" + self.__url + "/clip/v2/resource/" + type
      headers = {
        'hue-application-key': self.__token
      }
      response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        return response.json()["data"]
      else:
        logging.warning("Fail to get the " + type + " services from Hue Bridge. Status code: " + str(response.status_code))
        return []
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get the " + type + " services from Hue Bridge. Connection error.")
        return []
    
  # Get a service
  def getService(self, type="device", id=None):
    if not id:
      return {}
    try:
      url = "https://" + self.__url + "/clip/v2/resource/" + type + "/" + id
      headers = {
        'hue-application-key': self.__token
      }
      response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
      if response.status_code == 200:
        return response.json()
      else:
        logging.warning("Fail to get the " + type + " service with id " + id + " from Hue Bridge. Status code: " + str(response.status_code))
        return {}
    except (requests.ConnectionError, requests.Timeout) as exception:
        logging.warning("Fail to get the " + type + " service with id " + id + " from Hue Bridge. Connection error.")
        return {}
    
  # Set light service
  def updateLightService(self, id, properties):
    try:
      url = "https://" + self.__url + "/clip/v2/resource/light/" + id
      headers = {
        "Content-Type": "application/json",
        "hue-application-key": self.__token
      }
      response = requests.put(url, data = json.dumps(properties), headers = headers, verify=False, timeout=REQUEST_TIMEOUT)
      if not response.status_code == 200 and not response.status_code == 207:
        logging.warning("Fail to update the light service with id " + id + " in Hue Bridge. Status code: " + str(response.status_code))
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to update the light service with id " + id + " in Hue Bridge. Connection error.")
