import requests
import logging

class Hue:
  
  __url = "localhost"
  __token = "token"

  def __init__(self, url, token):
    self.__url = url
    self.__token = token
    if self.__url == "no_set":
      logging.error("HUE_HOST env var isn't set")
      exit()
    if self.__token == "no_set":
      logging.error("HUE_TOKEN env var isn't set")
      exit()
      
  # Get motion
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
        logging.warning("Fail to get Hue Bridge " + resource + ". Connection error.")
        self._fail_to_update = False
        return {}
