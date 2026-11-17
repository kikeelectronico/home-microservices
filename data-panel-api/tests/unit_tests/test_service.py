import json

import pytest

from service import DataPanelService


@pytest.fixture
def panel_service(mocker):
    result = DataPanelService(["lamp-1", "sensor-1"])
    result.initialize(mocker.MagicMock())
    return result


@pytest.mark.parametrize(
    ("topic", "payload", "expected"),
    [
        ("water/volume", b'{"liters": 12}', {"type": "water-volume", "data": {"liters": 12}}),
        ("meteo/warnings", b'["wind"]', {"type": "meteo-warnings", "data": ["wind"]}),
        ("meteo/weather", b'{"temperature": 18}', {"type": "meteo-weather", "data": {"temperature": 18}}),
        ("internet/status", b'{"online": true}', {"type": "internet-status", "data": {"online": True}}),
        ("electricity/grid", b'{"power": 100}', {"type": "electricity-grid", "data": {"power": 100}}),
        ("fire/nearest", b'{"distance": 5}', {"type": "fire-nearest", "data": {"distance": 5}}),
        ("device/lamp-1/on", b"true", {"type": "home", "data": {"lamp-1": True}}),
    ],
)
def test_handle_message_converts_supported_topics_to_events(panel_service, topic, payload, expected):
    panel_service._handle_message(topic, payload)

    assert panel_service.mqtt_events.get_nowait() == expected
    assert panel_service.mqtt_events.empty()


def test_handle_message_ignores_malformed_json(panel_service, caplog):
    panel_service._handle_message("water/volume", b"not-json")

    assert panel_service.mqtt_events.empty()
    assert "Invalid JSON payload" in caplog.text


def test_handle_message_ignores_unknown_topic(panel_service):
    panel_service._handle_message("unknown/topic", b'{"value": 1}')

    assert panel_service.mqtt_events.empty()


def test_request_initial_data_requests_topics_and_all_configured_devices(panel_service):
    panel_service.request_initial_data()

    assert [call.args for call in panel_service.mqtt_client.publish.call_args_list] == [
        ("water/volume/request", ""),
        ("meteo/warnings/request", ""),
        ("meteo/weather/request", ""),
        ("internet/status/request", ""),
        ("electricity/grid/request", ""),
        ("fire/nearest/request", ""),
        (
            "device/control",
            json.dumps({"id": "lamp-1", "param": "", "value": "", "intent": "request"}),
        ),
        (
            "device/control",
            json.dumps({"id": "sensor-1", "param": "", "value": "", "intent": "request"}),
        ),
    ]
