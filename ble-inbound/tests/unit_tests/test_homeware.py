import json

import pytest
import requests

import homeware
from homeware import Homeware


def test_execute_publishes_device_control_request(mocker):
    mqtt_client = mocker.MagicMock()
    client = Homeware(mqtt_client, "https://homeware.test", "api-key")

    client.execute("sensor_1", "online", True)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "sensor_1", "param": "online", "value": True, "intent": "execute"}),
    )


def test_get_returns_state_and_sends_authentication(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = True
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("sensor_1", "online") is True
    get.assert_called_once_with(
        "https://homeware.test/api/devices/sensor_1/states/online",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("status_code", [404, 503])
def test_get_returns_empty_dict_for_failed_http_status(mocker, monkeypatch, status_code, caplog):
    monkeypatch.setattr(
        homeware.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=status_code))
    )
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("sensor_1", "online") == {}
    assert f"Status code: {status_code}" in caplog.text


@pytest.mark.parametrize("network_error", [requests.ConnectionError, requests.Timeout])
def test_get_returns_empty_dict_on_network_error(mocker, monkeypatch, network_error, caplog):
    monkeypatch.setattr(homeware.requests, "get", mocker.MagicMock(side_effect=network_error))
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("sensor_1", "online") == {}
    assert "Connection error" in caplog.text
