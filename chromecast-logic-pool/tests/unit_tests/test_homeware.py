import json

import pytest
import requests

from homeware import Homeware
import homeware


def test_execute_publishes_homeware_control_payload(mocker):
    mqtt_client = mocker.MagicMock()
    client = Homeware(mqtt_client, "https://homeware.test", "api-key")

    client.execute("hue_17", "brightness", 20)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "hue_17", "param": "brightness", "value": 20, "intent": "execute"}),
    )


def test_get_returns_decoded_state_and_sends_authentication_header(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = 45
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_17", "brightness") == 45
    get.assert_called_once_with(
        "https://homeware.test/api/devices/hue_17/states/brightness",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("status_code", [404, 503])
def test_get_returns_empty_dict_for_unsuccessful_status(mocker, monkeypatch, status_code, caplog):
    monkeypatch.setattr(
        homeware.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=status_code))
    )
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_17", "brightness") == {}
    assert f"Status code: {status_code}" in caplog.text


@pytest.mark.parametrize("network_error", [requests.ConnectionError, requests.Timeout])
def test_get_returns_empty_dict_on_network_error(mocker, monkeypatch, network_error, caplog):
    monkeypatch.setattr(homeware.requests, "get", mocker.MagicMock(side_effect=network_error))
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_17", "brightness") == {}
    assert "Conection error" in caplog.text
