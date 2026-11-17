import logging

import requests
from lxml import html

WATER_URL = "https://www.embalses.net/comunidad-13-comunidad-de-madrid.html"
REQUEST_TIMEOUT = 10

def _first(items):
  return items[0] if items else None

def getWater(timeout=REQUEST_TIMEOUT):
  try:
    page = requests.get(WATER_URL, timeout=REQUEST_TIMEOUT)
    if page.status_code != 200:
      logging.warning("Fail to reach embalses.net. Status code: %s", page.status_code)
      return None

    tree = html.fromstring(page.content)
    last_update = str(_first(tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[1]/strong/text()'))).split("(")[1].split(")")[0]
    level = float(str(_first(tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[4]/strong/text()'))).replace(",","."))

    if not last_update or not level:
      logging.warning("Fail to parse embalses.net response.")
      return None
    return {
      "level": level,
      "last_update": last_update,
    }
  except Exception:
    logging.warning("Fail to reach embalses.net.")
    return None
