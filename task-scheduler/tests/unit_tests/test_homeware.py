import json

import pytest
import requests

from homeware import Homeware
import homeware


def test_execute_publishes_device_control_payload(mocker):
    mqtt_client = mocker.MagicMock()
    client = Homeware(mqtt_client, "https://homeware.test", "api-key")

    client.execute("thermostat_1", "thermostatMode", "heat")

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps(
            {"id": "thermostat_1", "param": "thermostatMode", "value": "heat", "intent": "execute"}
        ),
    )


def test_get_returns_decoded_status_and_uses_authorization(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = True
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("switch_at_home", "on") is True
    get.assert_called_once_with(
        "https://homeware.test/api/devices/switch_at_home/states/on",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [requests.ConnectionError, requests.Timeout])
def test_get_returns_empty_dict_on_network_error(mocker, monkeypatch, failure, caplog):
    monkeypatch.setattr(homeware.requests, "get", mocker.MagicMock(side_effect=failure))
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("switch_at_home", "on") == {}
    assert "Connection error" in caplog.text


def test_get_returns_empty_dict_on_http_error(mocker, monkeypatch, caplog):
    monkeypatch.setattr(
        homeware.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503))
    )
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("switch_at_home", "on") == {}
    assert "Status code: 503" in caplog.text
