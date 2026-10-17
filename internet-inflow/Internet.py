import logging
import requests

REQUEST_TIMEOUT = 10

def getInternetStatus():
  try:
    requests.get("https://www.google.com", timeout=REQUEST_TIMEOUT)
    return {
      "connected": True
    }
  except (requests.ConnectionError, requests.Timeout) as exception:
    logging.warning("Fail to reach Google. Conection error.")
    return {
      "connected": False
    }
