import logging
import requests

def getInternetStatus():
  try:
    requests.get("https://www.google.com", timeout=2)
    return {
      "connected": True
    }
  except (requests.ConnectionError, requests.Timeout) as exception:
    logging.warning("Fail to reach Google. Conection error.")
    return {
      "connected": False
    }
