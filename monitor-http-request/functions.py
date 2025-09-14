import requests
from requests.exceptions import ConnectionError
import logging

# Test both the API and the db getting the status of a device
def homewareTest(api_url, api_key):
  try:
    url = api_url + "/api/devices/scene_dim/states"
    headers = {
        "Authorization": "bearer " + api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      status = response.json()
      return "enable" in status
    else:
      logging.warning("Homeware response with " + response.status_code + " code")
      return False
  except ConnectionError:
    logging.warning("Unable to connect to Homeware")
    return False
  
# Test Hue Bridge
def hueTest(api_url, api_token):     
  try:
    url = "http://" + api_url + "/api/" +	api_token + "/lights"
    response = requests.get(url)
                
    if response.status_code == 200:
      return True
    else:
      logging.warning("Hue Bridge response with " + response.status_code + " code")
      return False
  except ConnectionError:
    logging.warning("Unable to connect to Hue Bridge")
    return False