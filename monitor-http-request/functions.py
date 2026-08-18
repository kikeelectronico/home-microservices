import requests
import logging

import urllib3
urllib3.disable_warnings()

REQUEST_TIMEOUT = 10

# Test both the API and the db getting the status of a device
def homewareTest(api_url, api_key):
  try:
    url = api_url + "/api/devices/scene_dim/states"
    headers = {
        "Authorization": "bearer " + api_key
    }

    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
      status = response.json()
      return "enable" in status
    else:
      logging.warning("Homeware response with " + str(response.status_code) + " code")
      return False
  except requests.ConnectionError:
    logging.warning("Unable to connect to Homeware")
    return False
  
# Test Hue Bridge
def hueTest(api_url, api_token):     
  try:
    url = "http://" + api_url + "/api/" +	api_token + "/lights"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
                
    if response.status_code == 200:
      return True
    else:
      logging.warning("Hue Bridge response with " + str(response.status_code) + " code")
      return False
  except requests.ConnectionError:
    logging.warning("Unable to connect to Hue Bridge")
    return False

# Test Ikea Bridge
def ikeaTest(api_url, api_token):     
  try:
    url = f"https://{api_url}:8443/v1/devices"
    headers = {
      "Authorization": f"Bearer {api_token}"
    }
    response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
      return True
    logging.warning("Fail to get devices from Ikea Bridge. Status code: " + str(response.status_code))
    return False
  except (requests.ConnectionError, requests.Timeout) as exception:
      logging.warning("Fail to get devices from Ikea Bridge. Connection error.")
      return False
