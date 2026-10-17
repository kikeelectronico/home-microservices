import logging
import time

import pychromecast

import logic
from constants import HEARTBEAT_TOPIC
from shutdown import stop_requested, wait_for_stop


class ChromecastLogicPoolService:

  def __init__(self):
    self.settings = None
    self.mqtt_client = None
    self.homeware = None
    self.last_heartbeat_timestamp = 0

  def initialize(self, settings, mqtt_client, homeware):
    self.settings = settings
    self.mqtt_client = mqtt_client
    self.homeware = homeware

  def run(self):
    device = None
    browser = None

    try:
      while not stop_requested():
        try:
          # Connect to the tv
          chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Tele"])
          if not chromecasts:
            raise Exception("Chromecast not found")
          device = chromecasts[0]
          device.wait()
          device_controller = device.media_controller
          # device_controller.block_until_active(5)
          while device.socket_client.is_connected and not stop_requested():
            # if device.app_display_name is not None:
            if device_controller.status.player_state in ["IDLE", "UNKNOWN", "PAUSED"]:
              logic.notPlayingLights(self.homeware)
            if device_controller.status.player_state == "PLAYING":
              logic.playingLights(self.homeware)

              # Send the heartbeat
              if time.time() - self.last_heartbeat_timestamp > 10:
                self.mqtt_client.publish(HEARTBEAT_TOPIC, self.settings.service_id)
                self.last_heartbeat_timestamp = time.time()

            wait_for_stop(5)
        except Exception:
          try:
            device.disconnect()
          except Exception:
            logging.info("Fail to force disconnect.")
          try:
            browser.stop_discovery()
          except Exception:
            logging.info("Fail to stop discovery.")

          logging.info("Chromecast connection lost. Reconnecting in 10s.")
          wait_for_stop(10)
    finally:
      self._disconnect(device, browser)

  def _disconnect(self, device, browser):
    try:
      if device is not None:
        device.disconnect()
    except Exception:
      logging.info("Fail to force disconnect.")
    try:
      if browser is not None:
        browser.stop_discovery()
    except Exception:
      logging.info("Fail to stop discovery.")
