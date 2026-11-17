import pytest
import requests

import weather


def test_get_weather_returns_current_and_forecast(mocker, monkeypatch):
    data = {"current": {"temp_c": 17}, "forecast": {"forecastday": []}, "location": {"name": "Madrid"}}
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = data
    request = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(weather.requests, "request", request)

    assert weather.getWeather("api-key", "Madrid") == {"current": data["current"], "forecast": data["forecast"]}
    request.assert_called_once_with(
        "GET",
        "https://api.weatherapi.com/v1/forecast.json?key=api-key&q=Madrid&days=2&aqi=yes",
        timeout=weather.REQUEST_TIMEOUT,
    )


@pytest.mark.parametrize("failure", [503, requests.ConnectionError(), requests.Timeout()], ids=["http", "connection", "timeout"])
def test_get_weather_returns_none_on_request_failure(failure, mocker, monkeypatch):
    request = mocker.MagicMock()
    if isinstance(failure, int):
        request.return_value.status_code = failure
    else:
        request.side_effect = failure
    monkeypatch.setattr(weather.requests, "request", request)

    assert weather.getWeather("key", "Madrid") is None


@pytest.mark.parametrize("data", [{}, {"current": {}}, {"forecast": {}}])
def test_get_weather_returns_none_if_required_sections_are_missing(data, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = data
    monkeypatch.setattr(weather.requests, "request", mocker.MagicMock(return_value=response))

    assert weather.getWeather("key", "Madrid") is None
