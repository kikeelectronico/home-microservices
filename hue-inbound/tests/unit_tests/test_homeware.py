import json
import pytest
import requests

import support

support.add_service_to_path()

import homeware


@pytest.fixture
def homeware_client(mocker):
    mqtt_client = mocker.MagicMock()
    return homeware.Homeware(mqtt_client, "http://homeware", "secret"), mqtt_client


def test_execute_publishes_control_payload(homeware_client):
    client, mqtt_client = homeware_client

    client.execute("lamp-1", "on", True)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "lamp-1", "param": "on", "value": True, "intent": "execute"}),
    )


def test_get_returns_json_for_success(homeware_client, monkeypatch, mocker):
    client, _ = homeware_client
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"on": True}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)

    assert client.get("lamp-1", "on") == {"on": True}
    get.assert_called_once_with(
        "http://homeware/api/devices/lamp-1/states/on",
        headers={"Authorization": "bearer secret"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize(
    "failure",
    [503, requests.Timeout()],
    ids=["http-error", "timeout"],
)
def test_get_returns_empty_dict_on_failure(homeware_client, monkeypatch, mocker, failure):
    client, _ = homeware_client
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(homeware.requests, "get", get)

    assert client.get("lamp-1", "on") == {}
