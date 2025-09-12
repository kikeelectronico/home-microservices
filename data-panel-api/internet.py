import requests
import logging

class Internet:

  _connected = True

  def __init__(self):

  def checkConnectivity(self):
    try:
      requests.get("https://www.google.com", timeout=2)
      self._connected = True
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to reach Google. Conection error.")
      self._connected = False
      
    try:
      requests.get("https://www.cloudflare.com/", timeout=2)
      self._connected = True
    except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to reach Cloudflare. Conection error.")
      self._connected = self._connected and False
    
    return self._connected

  def getConnected(self):
    return self._connected