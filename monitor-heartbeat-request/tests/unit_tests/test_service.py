from constants import HEARTBEAT_REQUEST_TOPIC
import service


def test_initialize_stores_mqtt_client():
    heartbeat_service = service.MonitorHeartbeatRequestService()
    client = object()

    heartbeat_service.initialize(client)

    assert heartbeat_service.mqtt_client is client


def test_publish_sends_heartbeat_request(mocker):
    client = mocker.MagicMock()
    heartbeat_service = service.MonitorHeartbeatRequestService()
    heartbeat_service.initialize(client)

    heartbeat_service.publish_heartbeat_request()

    client.publish.assert_called_once_with(HEARTBEAT_REQUEST_TOPIC, "are-you-there")
