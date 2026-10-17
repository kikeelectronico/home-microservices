import logging
import time

from constants import HEARTBEAT_TOPIC


class MonitorHeartbeatControlService:

  def __init__(self):
    self.homeware = None
    self.devices_heartbeats = {}

  def initialize(self, homeware):
    self.homeware = homeware

  def _handle_message(self, topic, payload):
    if topic == HEARTBEAT_TOPIC:
      service = payload.decode("utf-8")
      if service not in self.devices_heartbeats:
        logging.info(service + ": arriba")
      self.devices_heartbeats[service] = time.time()
      self.homeware.execute(service, "online", True)
