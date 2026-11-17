import pytest
import requests

import hue


@pytest.fixture
def bridge():
    return hue.Hue("bridge.local", "bridge-token")


def test_get_event_stream_client_uses_auth_and_returns_stream(bridge, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200, headers={"Content-Type": "text/event-stream"})
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(hue.requests, "get", get)
    monkeypatch.setattr(hue, "stop_requested", lambda: False)

    stream = bridge.getEventStreamClient()

    assert isinstance(stream, hue.HueEventStreamClient)
    get.assert_called_once_with(
        "https://bridge.local/eventstream/clip/v2",
        headers={"hue-application-key": "bridge-token", "Accept": "text/event-stream"},
        stream=True,
        verify=False,
    )
    stream.close()
    response.close.assert_called_once_with()


@pytest.mark.parametrize("response_headers", [{}, {"Content-Type": "application/json"}])
def test_event_stream_retries_and_closes_invalid_responses(bridge, response_headers, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200, headers=response_headers)
    monkeypatch.setattr(hue.requests, "get", mocker.MagicMock(return_value=response))
    monkeypatch.setattr(hue, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(hue, "wait_for_stop", wait_for_stop)

    assert bridge.getEventStreamClient() is None

    response.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(5)


def test_event_stream_retries_after_connection_error(bridge, mocker, monkeypatch):
    get = mocker.MagicMock(side_effect=[requests.ConnectionError(), mocker.MagicMock(status_code=503)])
    monkeypatch.setattr(hue.requests, "get", get)
    monkeypatch.setattr(hue, "stop_requested", mocker.MagicMock(side_effect=[False, False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(hue, "wait_for_stop", wait_for_stop)

    assert bridge.getEventStreamClient() is None

    assert get.call_count == 2
    assert [(call.args, call.kwargs) for call in wait_for_stop.call_args_list] == [((5,), {}), ((5,), {})]
