import json

import pytest
import requests

import Homeware


def test_execute_publishes_control_message(mocker):
    mqtt_client = mocker.MagicMock()
    homeware = Homeware.Homeware(mqtt_client, "http://homeware", "api-key")

    homeware.execute("scene_awake", "enable", False)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "scene_awake", "param": "enable", "value": False, "intent": "execute"}),
    )


def test_get_returns_response_json_and_authorizes(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = True
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(Homeware.requests, "get", get)
    homeware = Homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert homeware.get("scene_awake", "enable") is True
    get.assert_called_once_with(
        "http://homeware/api/devices/scene_awake/states/enable",
        headers={"Authorization": "bearer api-key"},
        timeout=Homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_returns_empty_dict_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(Homeware.requests, "get", get)
    homeware = Homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert homeware.get("scene_awake", "enable") == {}
