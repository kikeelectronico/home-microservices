import pytest

from constants import HEARTBEAT_TOPIC
import service


@pytest.fixture
def chromecast_service(mocker):
    result = service.ChromecastLogicPoolService()
    result.settings = mocker.MagicMock(service_id="chromecast-logic-pool-test")
    result.mqtt_client = mocker.MagicMock()
    result.homeware = mocker.MagicMock()
    return result


def test_run_applies_playing_logic_publishes_heartbeat_and_disconnects(
    chromecast_service, mocker, monkeypatch
):
    device = mocker.MagicMock()
    device.socket_client.is_connected = True
    device.media_controller.status.player_state = "PLAYING"
    browser = mocker.MagicMock()
    monkeypatch.setattr(
        service.pychromecast,
        "get_listed_chromecasts",
        mocker.MagicMock(return_value=([device], browser)),
    )
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, False, True, True]))
    monkeypatch.setattr(service, "wait_for_stop", mocker.MagicMock())
    monkeypatch.setattr(service.time, "time", mocker.MagicMock(side_effect=[11, 12]))
    playing = mocker.patch.object(service.logic, "playing_lights", return_value=True)

    chromecast_service.run()

    playing.assert_called_once_with(chromecast_service.homeware, False, {})
    assert chromecast_service.is_playing is True
    chromecast_service.mqtt_client.publish.assert_called_once_with(
        HEARTBEAT_TOPIC, "chromecast-logic-pool-test"
    )
    device.wait.assert_called_once_with()
    device.disconnect.assert_called_once_with()
    browser.stop_discovery.assert_called_once_with()


def test_run_calls_not_playing_logic_for_paused_state(chromecast_service, mocker, monkeypatch):
    device = mocker.MagicMock()
    device.socket_client.is_connected = True
    device.media_controller.status.player_state = "PAUSED"
    browser = mocker.MagicMock()
    monkeypatch.setattr(
        service.pychromecast,
        "get_listed_chromecasts",
        mocker.MagicMock(return_value=([device], browser)),
    )
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, False, True, True]))
    monkeypatch.setattr(service, "wait_for_stop", mocker.MagicMock())
    not_playing = mocker.patch.object(service.logic, "not_playing_lights", return_value=False)

    chromecast_service.run()

    not_playing.assert_called_once_with(chromecast_service.homeware, False, {})
    chromecast_service.mqtt_client.publish.assert_not_called()
    device.disconnect.assert_called_once_with()
    browser.stop_discovery.assert_called_once_with()


def test_disconnect_swallows_device_and_browser_cleanup_errors(chromecast_service, mocker):
    device = mocker.MagicMock()
    device.disconnect.side_effect = RuntimeError("device unavailable")
    browser = mocker.MagicMock()
    browser.stop_discovery.side_effect = RuntimeError("browser unavailable")

    chromecast_service._disconnect(device, browser)

    device.disconnect.assert_called_once_with()
    browser.stop_discovery.assert_called_once_with()
