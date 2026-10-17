import logging

import requests
from requests.exceptions import ConnectTimeout, ConnectionError

from constants import HEARTBEAT_TOPIC, REQUEST_TIMEOUT, SLEEP_TIME
from shutdown import stop_requested, wait_for_stop


class DNSUpdaterService:

  def __init__(self):
    self.settings = None
    self.mqtt_client = None
    self.last_ip = "unknown"

  def initialize(self, settings, mqtt_client):
    self.settings = settings
    self.mqtt_client = mqtt_client

  def _update_dns_if_needed(self):
    ip = requests.get(self.settings.get_ip_endpoint, timeout=REQUEST_TIMEOUT).text
    if not ip == self.last_ip and len(ip.split(".")) == 4:
      # Make an update request to the Cloudflare API
      url = "https://api.cloudflare.com/client/v4/zones/" + self.settings.cloudflare_zone + "/dns_records/" + self.settings.cloudflare_dns_id
      payload = "{\"content\": \"" + ip + "\"}"
      headers = {
        'Authorization': 'Bearer ' + self.settings.cloudflare_token,
        'Content-Type': 'application/json'
      }
      response = requests.request("PATCH", url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT).json()
      # Verify the response from Cloudflare
      if response["success"]:
        logging.info("IP de Homeware actualizada")
      else:
        logging.error("Problemas al actualizar la IP de Homeware")
        self.mqtt_client.publish("notificacion/text/alert", "Problemas al actualizar la IP de Homeware")
      self.last_ip = ip

  def run(self):
    while not stop_requested():
      try:
        # Get current public IP and update it if needed
        self._update_dns_if_needed()
        # Send heartbeat
        self.mqtt_client.publish(HEARTBEAT_TOPIC, self.settings.service_id)
      except ConnectTimeout:
        logging.info("Connection timeout")
      except ConnectionError:
        logging.info("Connection error")
      finally:
        # Wait until next iteration
        wait_for_stop(SLEEP_TIME)
