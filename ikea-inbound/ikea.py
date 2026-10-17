import json
import logging
import ssl
import threading
import time
import uuid

from websocket import WebSocketApp

from constants import WEBSOCKET_RECONNECT_DELAY
from shutdown import stop_requested, wait_for_stop


class Ikea:

  def __init__(self, host, token):
    self.__host = host
    self.__token = token

  def run_event_stream(self, message_handler):
    # Open WebSocket
    url = f"wss://{self.__host}:8443/v1"
    headers = {
      "Authorization": "Bearer " + self.__token
    }
    # Contexto SSL para certificado autofirmado
    sslopt = {"cert_reqs": ssl.CERT_NONE}
    while not stop_requested():
      def on_message(ws, message):
        message_handler(message)

      ws_app = WebSocketApp(
        url,
        header=[key + ": " + value for key, value in headers.items()],
        on_message=on_message,
        on_error=self._on_error,
        on_close=self._on_close,
        on_open=self._on_open,
      )
      try:
        ws_app.run_forever(sslopt=sslopt)
      except Exception as exc:
        logging.warning("IKEA WebSocket stopped with error: %s", exc)
      finally:
        try:
          ws_app.close()
        except Exception as exc:
          logging.warning("Fail to close IKEA WebSocket: %s", exc)
      if stop_requested():
        break
      logging.warning("IKEA WebSocket disconnected. Reconnecting in %ss", WEBSOCKET_RECONNECT_DELAY)
      wait_for_stop(WEBSOCKET_RECONNECT_DELAY)

  def _on_error(self, ws, error):
    logging.warning("IKEA WebSocket error: %s", error)

  def _on_close(self, ws, close_status_code, close_msg):
    logging.info("IKEA WebSocket closed")

  def _on_open(self, ws):
    logging.info("IKEA WebSocket opened")

    def run():
      while not stop_requested():
        ping_msg = {
          "id": str(uuid.uuid4()),
          "specversion": "1.1.0",
          "source": "urn:lpgera:dirigera",
          "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          "type": "ping",
          "data": None
        }
        try:
          ws.send(json.dumps(ping_msg))
        except Exception as exc:
          logging.warning("Fail to send IKEA WebSocket ping: %s", exc)
          break
        wait_for_stop(30)
      if stop_requested():
        ws.close()

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
