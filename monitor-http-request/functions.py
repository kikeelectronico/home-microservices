import requests
from requests.exceptions import ConnectionError

# Test both the API and the db getting the status of a device
def homewareTest(api_url, api_key, logger):
  try:
    url = api_url + "/api/status/get/scene_dim"
    headers = {
        "Authorization": "bearer " + api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      status = response.json()
      return "enable" in status
    else:
      logger.log_text("Homeware response with " + response.status_code + " code", severity="WARNING")
      return False
  except ConnectionError:
    logger.log_text("Unable to connect to Homeware", severity="WARNING")
    return False
  
# Test Hue Bridge
def hueTest(api_url, api_token, logger):     
  try:
    url = "http://" + api_url + "/api/" +	api_token + "/lights"
    response = requests.get(url)
                
    if response.status_code == 200:
      return True
    else:
      logger.log_text("Hue Bridge response with " + response.status_code + " code", severity="WARNING")
      return False
  except ConnectionError:
    logger.log_text("Unable to connect to Hue Bridge", severity="WARNING")
    return False