import json

import pytest
import requests

import homeware
from homeware import Homeware


def test_execute_publishes_device_control_payload(mocker):
    mqtt_client = mocker.MagicMock()
    client = Homeware(mqtt_client, "https://homeware.test", "api-key")

    client.execute("lamp-1", "on", True)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "lamp-1", "param": "on", "value": True, "intent": "execute"}),
    )


def test_get_returns_decoded_state_and_sends_authentication(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"enable": True}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("scene_winter", "enable") == {"enable": True}
    get.assert_called_once_with(
        "https://homeware.test/api/devices/scene_winter/states/enable",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [requests.ConnectionError, requests.Timeout])
def test_get_returns_empty_dict_on_network_error(mocker, monkeypatch, failure, caplog):
    monkeypatch.setattr(homeware.requests, "get", mocker.MagicMock(side_effect=failure))
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("scene_winter", "enable") == {}
    assert "Conection error" in caplog.text


def test_get_returns_empty_dict_on_http_error(mocker, monkeypatch, caplog):
    monkeypatch.setattr(
        homeware.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503))
    )
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("scene_winter", "enable") == {}
    assert "Status code: 503" in caplog.text
