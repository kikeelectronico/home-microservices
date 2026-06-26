import requests
import logging
from sseclient import SSEClient
import time

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

  def getEventStreamClient(self):
    while True:
      try:
        url = "https://" + self.__url + "/eventstream/clip/v2"
        headers = {
          'hue-application-key': self.__token,
          'Accept': 'text/event-stream'
        }
        stream_response = requests.get(url, headers=headers, stream=True, verify=False)
        if stream_response.status_code != 200:
          logging.warning("Fail to connect to Hue Bridge SSE. Status code: %s. Retrying in 5s", stream_response.status_code)
          time.sleep(5)
          continue
        content_type = stream_response.headers.get("Content-Type", "")
        if "text/event-stream" not in content_type:
          logging.warning("Fail to connect to Hue Bridge SSE. Invalid content type: %s. Retrying in 5s", content_type)
          time.sleep(5)
          continue
        return SSEClient(stream_response)
      except (requests.ConnectionError, requests.Timeout):
        logging.warning("Fail to connect to Hue Bridge SSE. Connection error. Retrying in 5s")
        time.sleep(5)
