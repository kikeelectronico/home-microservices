import logging
from datetime import date, datetime
import xml.etree.ElementTree as ElementTree

import requests


def relative_day(text: str) -> int:
  try:
    target_date = datetime.fromisoformat(text).date()
  except ValueError:
    return -1

  return (target_date - date.today()).days


def is_alert_active(start_text: str, end_text: str) -> bool:
  try:
    start_dt = datetime.fromisoformat(start_text)
    end_dt = datetime.fromisoformat(end_text)
  except ValueError:
    return False

  now = datetime.now(start_dt.tzinfo)

  return start_dt <= now <= end_dt


def getWarnings(rss_url, area, timeout=10):
  if rss_url == "no_set" or area == "no_set":
    logging.error("Warnings env vars aren't set")
    return None

  try:
    response = requests.get(rss_url, timeout=timeout)
    if response.status_code == 200:
      feed_data = response.text
    else:
      logging.warning("Fail to get AEMET RSS feed. Status code: %s", response.status_code)
      return None
  except (requests.ConnectionError, requests.Timeout):
    logging.warning("Fail to get AEMET RSS feed. Connection error.")
    return None

  warnings = []
  feed_root = ElementTree.fromstring(feed_data)
  channel = feed_root.find("channel")
  if channel is None:
    return None
  build_date = channel.findtext("lastBuildDate", default="")

  for item in channel.findall("item"):
    title = item.findtext("title", default="")
    if area in title:
      link = item.findtext("link", default="")
      if not link:
        continue

      try:
        response = requests.get(link, timeout=timeout)
        if response.status_code == 200:
          warning_data = response.text
        else:
          logging.warning("Fail to get AEMET warning. Status code: %s", response.status_code)
          continue
      except (requests.ConnectionError, requests.Timeout):
        logging.warning("Fail to get AEMET warning. Connection error.")
        continue

      warning_root = ElementTree.fromstring(warning_data)
      ns = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
      warning = {}

      for info in warning_root.findall("cap:info", ns):
        language = info.findtext("cap:language", default="", namespaces=ns)
        if language == "es-ES":
          warning["title"] = info.findtext("cap:headline", default="", namespaces=ns).split(area)[0]
          warning["description"] = info.findtext("cap:description", default="", namespaces=ns)
          warning["starts"] = info.findtext("cap:onset", default="", namespaces=ns)
          warning["ends"] = info.findtext("cap:expires", default="", namespaces=ns)
          warning["start_offset"] = relative_day(warning["starts"])
          warning["is_active"] = is_alert_active(warning["starts"], warning["ends"])

          for parameter in info.findall("cap:parameter", ns):
            value_name = parameter.findtext("cap:valueName", default="", namespaces=ns)
            if value_name == "AEMET-Meteoalerta nivel":
              warning["level"] = parameter.findtext("cap:value", default="", namespaces=ns)
            if value_name == "AEMET-Meteoalerta probabilidad":
              warning["probability"] = parameter.findtext("cap:value", default="", namespaces=ns)

      if warning:
        warnings.append(warning)

  return warnings, build_date
