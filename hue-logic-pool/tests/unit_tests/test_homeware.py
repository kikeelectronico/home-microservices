import json

import pytest
import requests

import homeware


def test_execute_publishes_control_message(mocker):
    mqtt_client = mocker.MagicMock()
    api = homeware.Homeware(mqtt_client, "http://homeware", "api-key")

    api.execute("hue_2", "brightness", 80)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "hue_2", "param": "brightness", "value": 80, "intent": "execute"}),
    )


def test_get_returns_state_and_uses_authorization(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"temperatureK": 2700}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.get("hue_2", "color") == {"temperatureK": 2700}
    get.assert_called_once_with(
        "http://homeware/api/devices/hue_2/states/color",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_returns_empty_dict_on_failure(failure, mocker, monkeypatch, caplog):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.get("hue_2", "on") == {}
    assert "Fail to get Homeware status" in caplog.text
