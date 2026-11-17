import pytest
import requests

import internet


def test_get_internet_status_returns_connected_and_uses_timeout(mocker, monkeypatch):
    get = mocker.MagicMock()
    monkeypatch.setattr(internet.requests, "get", get)

    assert internet.getInternetStatus() == {"connected": True}
    get.assert_called_once_with("https://www.google.com", timeout=internet.REQUEST_TIMEOUT)


@pytest.mark.parametrize("failure", [requests.ConnectionError(), requests.Timeout()])
def test_get_internet_status_returns_disconnected_on_request_error(failure, mocker, monkeypatch, caplog):
    monkeypatch.setattr(internet.requests, "get", mocker.MagicMock(side_effect=failure))

    assert internet.getInternetStatus() == {"connected": False}
    assert "Fail to reach Google" in caplog.text
