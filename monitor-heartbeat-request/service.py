from constants import HEARTBEAT_REQUEST_TOPIC


class MonitorHeartbeatRequestService:

  def __init__(self):
    self.mqtt_client = None

  def initialize(self, mqtt_client):
    self.mqtt_client = mqtt_client

  def publish_heartbeat_request(self):
    self.mqtt_client.publish(HEARTBEAT_REQUEST_TOPIC, "are-you-there")
