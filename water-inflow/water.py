import logging

import requests
from lxml import html


WATER_URL = "https://www.embalses.net/comunidad-13-comunidad-de-madrid.html"


def _first(items):
  return items[0] if items else None


def getWater(url=WATER_URL, timeout=10):
  try:
    page = requests.get(url, timeout=timeout)
    if page.status_code != 200:
      logging.warning("Fail to reach embalses.net. Status code: %s", page.status_code)
      return None

    tree = html.fromstring(page.content)
    last_update = str(_first(tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[1]/strong/text()')))
    level = str(_first(tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[4]/strong/text()'))).replace(",",".")

    if not last_update or not level:
      logging.warning("Fail to parse embalses.net response.")
      return None
    return {
      "level": float(level),
      "last_update": last_update.split("(")[1].split(")")[0],
    }
  except Exception:
    logging.warning("Fail to reach embalses.net.")
    return None
