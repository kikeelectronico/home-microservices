import json
import time

from constants import (
  REQUEST_TIMEOUT,
  WARNINGS_INTERVAL,
  WARNINGS_REQUEST_TOPIC,
  WARNINGS_TOPIC,
  WEATHER_INTERVAL,
  WEATHER_REQUEST_TOPIC,
  WEATHER_TOPIC
)
from weather import getWeather
from weather_warnings import getWarnings


class MeteoInflowService:

  def __init__(self, settings):
    self.settings = settings
    self.mqtt_client = None
    self.last_warnings_timestamp = 0
    self.last_weather_timestamp = 0
    self.last_warnings_payload = {}
    self.last_weather_payload = {}

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def update_if_due(self):
    now = time.time()
    if now - self.last_warnings_timestamp > WARNINGS_INTERVAL:
      self._publish_warnings()
      self.last_warnings_timestamp = now

    if now - self.last_weather_timestamp > WEATHER_INTERVAL:
      self._publish_weather()
      self.last_weather_timestamp = now

  def _publish_warnings(self, force=False):
    warnings_payload = getWarnings(
      self.settings.aemet_rss,
      self.settings.aemet_area,
      REQUEST_TIMEOUT
    )
    if not warnings_payload:
      return

    if force or warnings_payload != self.last_warnings_payload:
      self.mqtt_client.publish(WARNINGS_TOPIC, json.dumps(warnings_payload))
      self.last_warnings_payload = warnings_payload

  def _publish_weather(self, force=False):
    weather_payload = getWeather(
      self.settings.wheather_api_key,
      self.settings.wheather_query
    )
    if not weather_payload:
      return

    if force or weather_payload != self.last_weather_payload:
      self.mqtt_client.publish(WEATHER_TOPIC, json.dumps(weather_payload))
      self.last_weather_payload = weather_payload

  def _handle_message(self, topic, payload):
    if topic == WARNINGS_REQUEST_TOPIC:
      self._publish_warnings(force=True)
    elif topic == WEATHER_REQUEST_TOPIC:
      self._publish_weather(force=True)
