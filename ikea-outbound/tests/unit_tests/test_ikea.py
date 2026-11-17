import pytest
import requests

import ikea


@pytest.fixture
def bridge():
    return ikea.Ikea("ikea.local", "secret")


def test_get_devices_returns_response_and_sets_auth(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = [{"id": "device-1"}]
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(ikea.requests, "get", get)

    assert bridge.getDevices() == [{"id": "device-1"}]
    get.assert_called_once_with(
        "https://ikea.local:8443/v1/devices",
        headers={"Authorization": "Bearer secret"},
        verify=False,
        timeout=ikea.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_devices_returns_empty_list_on_failure(bridge, failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(ikea.requests, "get", get)

    assert bridge.getDevices() == []


def test_get_device_returns_empty_dict_without_id(bridge, mocker, monkeypatch):
    get = mocker.MagicMock()
    monkeypatch.setattr(ikea.requests, "get", get)

    assert bridge.getDevice() == {}
    get.assert_not_called()


def test_get_device_returns_json_for_success(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"id": "device-1"}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(ikea.requests, "get", get)

    assert bridge.getDevice("device-1") == {"id": "device-1"}
    get.assert_called_once_with(
        "https://ikea.local:8443/v1/devices/device-1",
        headers={"Authorization": "Bearer secret"},
        verify=False,
        timeout=ikea.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize(("status", "expected"), [(202, True), (200, False)])
def test_update_device_sends_attribute_patch(bridge, status, expected, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=status)
    patch = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(ikea.requests, "patch", patch)

    assert bridge.updateDeviceAttribute("device-1", "isOn", True) is expected
    patch.assert_called_once_with(
        "https://ikea.local:8443/v1/devices/device-1",
        json=[{"attributes": {"isOn": True}}],
        headers={"Authorization": "Bearer secret"},
        verify=False,
        timeout=ikea.REQUEST_TIMEOUT,
    )
    response.raise_for_status.assert_called_once_with()


def test_update_device_handles_connection_error(bridge, mocker, monkeypatch, caplog):
    monkeypatch.setattr(ikea.requests, "patch", mocker.MagicMock(side_effect=requests.ConnectionError()))

    assert bridge.updateDeviceAttribute("device-1", "isOn", False) is False
    assert "Connection error" in caplog.text


def test_update_device_propagates_http_error_from_response(bridge, mocker, monkeypatch):
    response = mocker.MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("bad response")
    monkeypatch.setattr(ikea.requests, "patch", mocker.MagicMock(return_value=response))

    with pytest.raises(requests.HTTPError, match="bad response"):
        bridge.updateDeviceAttribute("device-1", "isOn", False)
