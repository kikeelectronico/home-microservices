import pytest
import requests

import hue


@pytest.fixture
def bridge():
    return hue.Hue("bridge.local", "hue-key")


def test_get_services_returns_data(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"data": [{"id": "device-1"}]}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices("motion") == [{"id": "device-1"}]
    get.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/motion",
        headers={"hue-application-key": "hue-key"},
        verify=False,
        timeout=hue.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.Timeout()], ids=["http-error", "timeout"])
def test_get_services_returns_empty_list_on_failure(bridge, failure, mocker, monkeypatch):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices() == []


def test_event_stream_client_returns_for_valid_response(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200, headers={"Content-Type": "text/event-stream"})
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)
    monkeypatch.setattr(hue, "stop_requested", lambda: False)

    stream = bridge.getEventStreamClient()

    assert isinstance(stream, hue.HueEventStreamClient)
    get.assert_called_once_with(
        "https://bridge.local/eventstream/clip/v2",
        headers={"hue-application-key": "hue-key", "Accept": "text/event-stream"},
        stream=True,
        verify=False,
    )
    stream.close()
    response.close.assert_called_once_with()


def test_event_stream_retries_and_closes_bad_response(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200, headers={"Content-Type": "application/json"})
    monkeypatch.setattr(hue.requests, "get", mocker.MagicMock(return_value=response))
    monkeypatch.setattr(hue, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(hue, "wait_for_stop", wait_for_stop)

    assert bridge.getEventStreamClient() is None

    response.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(5)
