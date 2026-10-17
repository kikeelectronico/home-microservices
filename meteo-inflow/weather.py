import logging
import requests

API_URL = "https://api.weatherapi.com/v1/forecast.json"
REQUEST_TIMEOUT = 10

def getWeather(api_key, query):
  try:
    url = f"{API_URL}?key={api_key}&q={query}&days=2&aqi=yes"

    response = requests.request("GET", url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
      weather = response.json()
    else:
      logging.warning("Fail to update weather data. Status code: %s", response.status_code)
      return None
  except (requests.ConnectionError, requests.Timeout):
    logging.warning("Fail to update weather data. Connection error.")
    return None

  if "current" not in weather or "forecast" not in weather:
    return None

  return {
    "current": weather["current"],
    "forecast": weather["forecast"],
  }
