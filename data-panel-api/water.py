import time
from lxml import html
import requests
import logging

RELOAD_TIME = 86400

class Water:

  _level = -1
  _last_update = "No date"
  _last_request = 0

  def __init__(self):
    pass

  def updateWater(self):
    try:
      page = requests.get("https://www.embalses.net/comunidad-13-comunidad-de-madrid.html")
      tree = html.fromstring(page.content)
      self._last_update = tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[1]/strong/text()')[0]
      self._last_update = self._last_update.split("(")[1].split(")")[0]
      self._level = tree.xpath('//*[@id="index_bodycenter"]/div[2]/div[2]/div[3]/div[4]/strong/text()')[0]
      self._level = float(self._level)
    except:
      logging.warning("Fail to reach embalses.net.")

  def getWater(self):
    now = time.time()
    if now - self._last_request > RELOAD_TIME:
      self._last_request = now
      self.updateWater()
    return {
      "level": self._level,
      "last_update": self._last_update
    }