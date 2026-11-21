import json
from types import SimpleNamespace

import pytest

from constants import (
    WEATHER_INTERVAL,
    WEATHER_REQUEST_TOPIC,
    WEATHER_TOPIC,
    WARNINGS_INTERVAL,
    WARNINGS_REQUEST_TOPIC,
    WARNINGS_TOPIC,
)
import service


@pytest.fixture
def meteo_service(mocker):
    settings = SimpleNamespace(
        aemet_rss="https://aemet/rss",
        aemet_area="Madrid",
        wheather_api_key="weather-key",
        wheather_query="Madrid",
    )
    instance = service.MeteoInflowService(settings)
    instance.initialize(mocker.MagicMock())
    return instance


def test_update_if_due_fetches_and_publishes_both_payloads(meteo_service, mocker, monkeypatch):
    warnings = [{"title": "Alerta"}]
    weather = {"current": {"temp_c": 18}, "forecast": {}}
    get_warnings = mocker.MagicMock(return_value=warnings)
    get_weather = mocker.MagicMock(return_value=weather)
    monkeypatch.setattr(service, "getWarnings", get_warnings)
    monkeypatch.setattr(service, "getWeather", get_weather)
    monkeypatch.setattr(service.time, "time", lambda: max(WARNINGS_INTERVAL, WEATHER_INTERVAL) + 1)

    meteo_service.update_if_due()

    get_warnings.assert_called_once_with("https://aemet/rss", "Madrid", service.REQUEST_TIMEOUT)
    get_weather.assert_called_once_with("weather-key", "Madrid")
    assert [(call.args, call.kwargs) for call in meteo_service.mqtt_client.publish.call_args_list] == [
        ((WARNINGS_TOPIC, json.dumps(warnings)), {}),
        ((WEATHER_TOPIC, json.dumps(weather)), {}),
    ]
    assert meteo_service.last_warnings_payload == warnings
    assert meteo_service.last_weather_payload == weather


def test_update_if_due_skips_fetch_until_intervals_expire(meteo_service, mocker, monkeypatch):
    get_warnings = mocker.patch.object(service, "getWarnings")
    get_weather = mocker.patch.object(service, "getWeather")
    monkeypatch.setattr(service.time, "time", lambda: min(WARNINGS_INTERVAL, WEATHER_INTERVAL))

    meteo_service.update_if_due()

    get_warnings.assert_not_called()
    get_weather.assert_not_called()
    meteo_service.mqtt_client.publish.assert_not_called()


@pytest.mark.parametrize("source", ["warnings", "weather"])
def test_duplicate_payload_is_not_republished(meteo_service, mocker, monkeypatch, source):
    payload = [{"title": "Alert"}] if source == "warnings" else {"current": {"temp_c": 18}}
    if source == "warnings":
        meteo_service.last_warnings_payload = payload
        monkeypatch.setattr(service, "getWarnings", mocker.MagicMock(return_value=payload.copy()))
        meteo_service._publish_warnings()
    else:
        meteo_service.last_weather_payload = payload
        monkeypatch.setattr(service, "getWeather", mocker.MagicMock(return_value=payload.copy()))
        meteo_service._publish_weather()

    meteo_service.mqtt_client.publish.assert_not_called()


@pytest.mark.parametrize("topic", [WARNINGS_REQUEST_TOPIC, WEATHER_REQUEST_TOPIC])
def test_request_topic_forces_matching_update(meteo_service, mocker, monkeypatch, topic):
    warnings_payload = [{"title": "Alert"}]
    weather_payload = {"current": {"temp_c": 18}}
    get_warnings = mocker.MagicMock(return_value=warnings_payload)
    get_weather = mocker.MagicMock(return_value=weather_payload)
    monkeypatch.setattr(service, "getWarnings", get_warnings)
    monkeypatch.setattr(service, "getWeather", get_weather)

    meteo_service._handle_message(topic, b"request")

    if topic == WARNINGS_REQUEST_TOPIC:
        get_warnings.assert_called_once_with("https://aemet/rss", "Madrid", service.REQUEST_TIMEOUT)
        get_weather.assert_not_called()
        meteo_service.mqtt_client.publish.assert_called_once_with(WARNINGS_TOPIC, json.dumps(warnings_payload))
    else:
        get_warnings.assert_not_called()
        get_weather.assert_called_once_with("weather-key", "Madrid")
        meteo_service.mqtt_client.publish.assert_called_once_with(WEATHER_TOPIC, json.dumps(weather_payload))


def test_empty_source_responses_are_not_published(meteo_service, mocker, monkeypatch):
    monkeypatch.setattr(service, "getWarnings", mocker.MagicMock(return_value=None))
    monkeypatch.setattr(service, "getWeather", mocker.MagicMock(return_value=None))

    meteo_service._publish_warnings(force=True)
    meteo_service._publish_weather(force=True)

    meteo_service.mqtt_client.publish.assert_not_called()


def test_unrelated_request_topic_is_ignored(meteo_service, mocker, monkeypatch):
    get_warnings = mocker.patch.object(service, "getWarnings")
    get_weather = mocker.patch.object(service, "getWeather")

    meteo_service._handle_message("other/topic", b"request")

    get_warnings.assert_not_called()
    get_weather.assert_not_called()
