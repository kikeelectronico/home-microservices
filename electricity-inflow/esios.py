import logging
import requests
from datetime import datetime, timedelta

API_URL = "https://api.esios.ree.es/indicators"
REQUEST_TIMEOUT = 10

def getEsiosIndicator(api_key, id):
  try:
    now = datetime.utcnow()
    start = now - timedelta(minutes=1)

    url = f"{API_URL}/{id}?start_date={start.isoformat()}Z&locale=es"
    headers = {
      "Accept": "application/json; application/vnd.esios-api-v1+json",
      "Content-Type": "application/json",
      "x-api-key": api_key
    }

    response = requests.request("GET", url, headers=headers, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
      indicator = response.json()["indicator"]
      values = indicator.get("values", None)
      last_reading = values[-1] if values and len(values) > 0 else None
      last_value = round(last_reading.get("value", None), 1)
      return {
        "co2_free_generation_percentege": last_value
      }
    else:
      logging.warning("Fail to update weather data. Status code: %s", response.status_code)
      return None
  except Exception:
    logging.warning("Fail to reach embalses.net.")
    return None
