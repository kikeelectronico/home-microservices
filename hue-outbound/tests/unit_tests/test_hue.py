import json

import pytest
import requests

import hue


@pytest.fixture
def bridge():
    return hue.Hue("bridge.local", "hue-secret")


def test_get_services_returns_data_and_uses_bridge_auth(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"data": [{"id": "device-1"}]}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices(type="light") == [{"id": "device-1"}]
    get.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/light",
        headers={"hue-application-key": "hue-secret"},
        verify=False,
        timeout=hue.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("result", [{}, {"data": []}])
def test_get_services_returns_empty_list_without_data(bridge, mocker, monkeypatch, result):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = result
    monkeypatch.setattr(hue.requests, "get", mocker.MagicMock(return_value=response))

    assert bridge.getServices() == []


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_services_returns_empty_list_on_error(bridge, failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices() == []


def test_get_service_returns_first_record(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"data": [{"id": "light-1"}, {"id": "light-2"}]}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getService("light", "light-1") == {"id": "light-1"}
    get.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/light/light-1",
        headers={"hue-application-key": "hue-secret"},
        verify=False,
        timeout=hue.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("data", [[], [{"ignored": True}]])
def test_get_service_returns_empty_dict_when_missing_or_id_absent(bridge, data, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"data": data}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getService("light", None) == {}
    get.assert_not_called()

    assert bridge.getService("light", "missing") == (data[0] if data else {})


@pytest.mark.parametrize("status", [200, 207])
def test_update_light_service_accepts_hue_success_statuses(bridge, status, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=status)
    put = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "put", put)
    properties = {"on": {"on": True}}

    bridge.updateLightService("light-1", properties)

    put.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/light/light-1",
        data=json.dumps(properties),
        headers={"Content-Type": "application/json", "hue-application-key": "hue-secret"},
        verify=False,
        timeout=hue.REQUEST_TIMEOUT,
    )


def test_update_light_service_logs_http_error(bridge, mocker, monkeypatch, caplog):
    response = mocker.MagicMock(status_code=500)
    monkeypatch.setattr(hue.requests, "put", mocker.MagicMock(return_value=response))

    bridge.updateLightService("light-1", {"on": {"on": False}})

    assert "Status code: 500" in caplog.text


def test_update_light_service_handles_connection_error(bridge, mocker, monkeypatch, caplog):
    monkeypatch.setattr(hue.requests, "put", mocker.MagicMock(side_effect=requests.ConnectionError()))

    bridge.updateLightService("light-1", {"on": {"on": False}})

    assert "Connection error" in caplog.text
