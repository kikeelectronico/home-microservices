import requests
import logging

class Hue:
  
  __url = "localhost"
  __token = "token"

  def __init__(self, url, token):
    self.__url = url
    self.__token = token
      
  # Get motion
  def getResource(self, resource="device"):
    if self.__token == "no_set" or self.__url == "no_set":
      self._fail_to_update = True
      logging.error("Hue env vars aren't set")
    else:
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