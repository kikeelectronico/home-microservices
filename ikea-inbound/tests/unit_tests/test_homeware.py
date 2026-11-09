import json

import pytest
import requests

import homeware


def test_execute_publishes_control_payload(mocker):
    client = mocker.MagicMock()
    api = homeware.Homeware(client, "http://homeware", "secret")

    api.execute("outlet-1", "on", True)

    client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "outlet-1", "param": "on", "value": True, "intent": "execute"}),
    )


def test_publish_emits_device_state_topic(mocker):
    client = mocker.MagicMock()
    api = homeware.Homeware(client, "http://homeware", "secret")

    api.publish("outlet-1", "voltage", 230.1)

    client.publish.assert_called_once_with("device/outlet-1/voltage", 230.1)


def test_get_returns_json_for_success(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"online": True}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "secret")

    assert api.get("outlet-1", "online") == {"online": True}
    get.assert_called_once_with(
        "http://homeware/api/devices/outlet-1/states/online",
        headers={"Authorization": "bearer secret"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_returns_empty_dict_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "secret")

    assert api.get("outlet-1", "online") == {}
