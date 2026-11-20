import json

import requests

from homeware import Homeware
import homeware


def test_execute_publishes_device_control_payload(mocker):
    mqtt_client = mocker.MagicMock()
    client = Homeware(mqtt_client, "https://homeware.test", "api-key")

    client.execute("lamp-1", "color", {"temperatureK": 3500})

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps(
            {
                "id": "lamp-1",
                "param": "color",
                "value": {"temperatureK": 3500},
                "intent": "execute",
            }
        ),
    )


def test_get_returns_decoded_state_and_uses_authentication(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"emergencia": False}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_15", "currentToggleSettings") == {"emergencia": False}
    get.assert_called_once_with(
        "https://homeware.test/api/devices/hue_15/states/currentToggleSettings",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


def test_get_returns_empty_dict_when_request_fails(mocker, monkeypatch, caplog):
    get = mocker.MagicMock(side_effect=requests.ConnectionError("offline"))
    monkeypatch.setattr(homeware.requests, "get", get)
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_15", "enable") == {}
    assert "Conection error" in caplog.text


def test_get_returns_empty_dict_for_non_success_status(mocker, monkeypatch, caplog):
    monkeypatch.setattr(
        homeware.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503))
    )
    client = Homeware(mocker.MagicMock(), "https://homeware.test", "api-key")

    assert client.get("hue_15", "enable") == {}
    assert "Status code: 503" in caplog.text
