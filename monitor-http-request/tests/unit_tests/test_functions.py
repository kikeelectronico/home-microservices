import pytest
import requests

import functions


def test_homeware_test_checks_state_endpoint_and_enable_field(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"enable": True}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.homeware_test("http://homeware", "key") is True
    get.assert_called_once_with(
        "http://homeware/api/devices/scene_dim/states",
        headers={"Authorization": "bearer key"},
        timeout=functions.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("response_body", [{}, {"on": True}])
def test_homeware_test_returns_false_when_enable_is_missing(response_body, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = response_body
    monkeypatch.setattr(functions.requests, "get", mocker.MagicMock(return_value=response))

    assert functions.homeware_test("http://homeware", "key") is False


@pytest.mark.parametrize("failure", [503, requests.ConnectionError()], ids=["http-error", "connection-error"])
def test_homeware_test_returns_false_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.homeware_test("http://homeware", "key") is False


def test_hue_test_requests_device_resource_with_bridge_token(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.hue_test("bridge.local", "hue-key") is True
    get.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/device",
        headers={"hue-application-key": "hue-key"},
        verify=False,
        timeout=functions.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [401, requests.Timeout()], ids=["http-error", "timeout"])
def test_hue_test_returns_false_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.hue_test("bridge.local", "hue-key") is False


def test_ikea_test_requests_devices_with_bearer_token(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.ikea_test("ikea.local", "ikea-key") is True
    get.assert_called_once_with(
        "https://ikea.local:8443/v1/devices",
        headers={"Authorization": "Bearer ikea-key"},
        verify=False,
        timeout=functions.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [404, requests.ConnectionError()], ids=["http-error", "connection-error"])
def test_ikea_test_returns_false_on_failure(failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.ikea_test("ikea.local", "ikea-key") is False
