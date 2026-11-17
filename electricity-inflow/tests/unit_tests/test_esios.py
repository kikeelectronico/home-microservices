from datetime import datetime

import pytest
import requests

import esios


def test_get_indicator_builds_recent_query_and_rounds_last_value(mocker, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def utcnow(cls):
            return cls(2026, 11, 16, 12, 30, 0)

    monkeypatch.setattr(esios, "datetime", FixedDateTime)
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"indicator": {"values": [{"value": 24.21}, {"value": 45.67}]}}
    request = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(esios.requests, "request", request)

    assert esios.getEsiosIndicator("api-key", 10033) == {"co2_free_generation_percentege": 45.7}
    request.assert_called_once_with(
        "GET",
        "https://api.esios.ree.es/indicators/10033?start_date=2026-11-16T12:29:00Z&locale=es",
        headers={
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "Content-Type": "application/json",
            "x-api-key": "api-key",
        },
        timeout=esios.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.ConnectionError(), requests.Timeout()], ids=["http", "connection", "timeout"])
def test_get_indicator_returns_none_on_api_failure(failure, mocker, monkeypatch, caplog):
    request = mocker.MagicMock()
    if isinstance(failure, int):
        request.return_value.status_code = failure
    else:
        request.side_effect = failure
    monkeypatch.setattr(esios.requests, "request", request)

    assert esios.getEsiosIndicator("key", 10033) is None
    assert caplog.records


@pytest.mark.parametrize("payload", [{}, {"indicator": {}}, {"indicator": {"values": []}}])
def test_get_indicator_returns_none_if_value_list_is_missing_or_empty(payload, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = payload
    monkeypatch.setattr(esios.requests, "request", mocker.MagicMock(return_value=response))

    assert esios.getEsiosIndicator("key", 10033) is None
