import pytest
import requests

import support

support.add_service_to_path()

import hue


@pytest.fixture
def bridge():
    return hue.Hue("bridge.local", "hue-secret")


def test_get_services_returns_data_and_uses_bridge_auth(bridge, monkeypatch, mocker):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"data": [{"id": "svc-1"}]}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices("motion") == [{"id": "svc-1"}]
    get.assert_called_once_with(
        "https://bridge.local/clip/v2/resource/motion",
        headers={"hue-application-key": "hue-secret"},
        verify=False,
        timeout=hue.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize(
    "failure",
    [500, requests.ConnectionError()],
    ids=["http-error", "connection-error"],
)
def test_get_services_returns_empty_list_on_failure(bridge, monkeypatch, mocker, failure):
    get = mocker.MagicMock()
    if isinstance(failure, int):
        get.return_value.status_code = failure
    else:
        get.side_effect = failure
    monkeypatch.setattr(hue.requests, "get", get)

    assert bridge.getServices() == []


def test_event_stream_client_is_returned_for_valid_response(bridge, monkeypatch, mocker):
    response = mocker.MagicMock(status_code=200, headers={"Content-Type": "text/event-stream"})
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)
    monkeypatch.setattr(hue, "stop_requested", lambda: False)

    stream = bridge.getEventStreamClient()

    assert isinstance(stream, hue.HueEventStreamClient)
    assert list(stream.events()) == list(response.iter_lines.return_value)
    get.assert_called_once_with(
        "https://bridge.local/eventstream/clip/v2",
        headers={"hue-application-key": "hue-secret", "Accept": "text/event-stream"},
        stream=True,
        verify=False,
    )
    stream.close()
    response.close.assert_called_once_with()


def test_event_stream_retries_and_closes_invalid_response(bridge, monkeypatch, mocker):
    response = mocker.MagicMock(status_code=200, headers={"Content-Type": "application/json"})
    monkeypatch.setattr(hue.requests, "get", mocker.MagicMock(return_value=response))
    stop_requested = mocker.MagicMock(side_effect=[False, True])
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(hue, "stop_requested", stop_requested)
    monkeypatch.setattr(hue, "wait_for_stop", wait_for_stop)

    assert bridge.getEventStreamClient() is None

    response.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(5)
