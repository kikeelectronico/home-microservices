import json

import pytest
import requests

import homeware


def test_execute_publishes_control_payload(mocker):
    client = mocker.MagicMock()
    api = homeware.Homeware(client, "http://homeware", "api-key")

    api.execute("switch_at_home", "on", False)

    client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "switch_at_home", "param": "on", "value": False, "intent": "execute"}),
    )


def test_get_returns_json_for_success(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = False
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.get("switch_at_home", "on") is False
    get.assert_called_once_with(
        "http://homeware/api/devices/switch_at_home/states/on",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.ConnectionError()], ids=["http-error", "connection-error"])
def test_get_returns_empty_dict_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.get("switch_at_home", "on") == {}


def test_get_devices_maps_devices_by_id(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = [{"id": "sensor-1"}, {"id": "sensor-2"}]
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(homeware.requests, "get", get)
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.getDevices() == (True, {"sensor-1": {"id": "sensor-1"}, "sensor-2": {"id": "sensor-2"}})
    get.assert_called_once_with(
        "http://homeware/api/devices",
        headers={"Authorization": "bearer api-key"},
        timeout=homeware.REQUEST_TIMEOUT,
    )


def test_get_devices_returns_failure_tuple_for_http_error(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=503)
    monkeypatch.setattr(homeware.requests, "get", mocker.MagicMock(return_value=response))
    api = homeware.Homeware(mocker.MagicMock(), "http://homeware", "api-key")

    assert api.getDevices() == (False, {})
