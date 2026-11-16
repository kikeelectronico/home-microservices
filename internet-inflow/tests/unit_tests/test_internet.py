import pytest
import requests

import Internet


def test_get_internet_status_returns_connected_and_uses_timeout(mocker, monkeypatch):
    get = mocker.MagicMock()
    monkeypatch.setattr(Internet.requests, "get", get)

    assert Internet.getInternetStatus() == {"connected": True}
    get.assert_called_once_with("https://www.google.com", timeout=Internet.REQUEST_TIMEOUT)


@pytest.mark.parametrize("failure", [requests.ConnectionError(), requests.Timeout()])
def test_get_internet_status_returns_disconnected_on_request_error(failure, mocker, monkeypatch, caplog):
    monkeypatch.setattr(Internet.requests, "get", mocker.MagicMock(side_effect=failure))

    assert Internet.getInternetStatus() == {"connected": False}
    assert "Fail to reach Google" in caplog.text
