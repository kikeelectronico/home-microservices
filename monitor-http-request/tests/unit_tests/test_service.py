from types import SimpleNamespace

import pytest

from constants import BLOCK_TIME, HEARTBEAT_TOPIC, SLEEP_TIME, TEXT_ALERT_TOPIC, VOICE_ALERT_TOPIC
import service


@pytest.fixture
def monitor(mocker):
    settings = SimpleNamespace(
        homeware_api_url="http://homeware",
        homeware_api_key="homeware-key",
        hue_host="bridge.local",
        hue_token="hue-key",
        ikea_host="ikea.local",
        ikea_token="ikea-key",
        service_id="monitor-http-request-test",
    )
    return service.MonitorHttpRequestService(settings, mocker.MagicMock())


def test_all_services_available_publishes_heartbeat_and_returns_sleep_time(monitor, monkeypatch):
    monkeypatch.setattr(service.functions, "homeware_test", lambda *_: True)
    monkeypatch.setattr(service.functions, "hue_test", lambda *_: True)
    monkeypatch.setattr(service.functions, "ikea_test", lambda *_: True)

    assert monitor.check_connections() == SLEEP_TIME
    monitor.mqtt_client.publish.assert_called_once_with(HEARTBEAT_TOPIC, "monitor-http-request-test")


@pytest.mark.parametrize(
    ("failed_check", "expected_alert", "checked"),
    [
        ("homeware_test", "Homeware no responde", ["homeware_test"]),
        ("hue_test", "Hue bridge no responde", ["homeware_test", "hue_test"]),
        ("ikea_test", "Ikea bridge no responde", ["homeware_test", "hue_test", "ikea_test"]),
    ],
)
def test_failed_check_sends_alerts_and_short_circuits(monitor, monkeypatch, mocker, failed_check, expected_alert, checked):
    checks = {name: mocker.MagicMock(return_value=True) for name in ("homeware_test", "hue_test", "ikea_test")}
    checks[failed_check].return_value = False
    for name, check in checks.items():
        monkeypatch.setattr(service.functions, name, check)

    assert monitor.check_connections() == BLOCK_TIME

    for name in checked:
        checks[name].assert_called_once()
    for name in {"homeware_test", "hue_test", "ikea_test"} - set(checked):
        checks[name].assert_not_called()
    assert [(call.args, call.kwargs) for call in monitor.mqtt_client.publish.call_args_list] == [
        ((VOICE_ALERT_TOPIC, expected_alert), {}),
        ((TEXT_ALERT_TOPIC, expected_alert), {}),
    ]
