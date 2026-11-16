from datetime import date, datetime

import pytest
import requests

import weather_warnings


def test_relative_day_returns_delta_from_today(monkeypatch):
    class FrozenDate:
        @classmethod
        def today(cls):
            return date(2026, 11, 16)

    monkeypatch.setattr(weather_warnings, "date", FrozenDate)

    assert weather_warnings.relative_day("2026-11-18T12:00:00+00:00") == 2
    assert weather_warnings.relative_day("not-a-date") == -1


def test_is_alert_active_checks_inclusive_start_and_end(monkeypatch):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 16, 12, 0, tzinfo=tz)

    monkeypatch.setattr(weather_warnings, "datetime", FrozenDateTime)

    assert weather_warnings.is_alert_active("2026-11-16T12:00:00+00:00", "2026-11-16T13:00:00+00:00") is True
    assert weather_warnings.is_alert_active("2026-11-16T13:00:00+00:00", "2026-11-16T14:00:00+00:00") is False
    assert weather_warnings.is_alert_active("bad-date", "also-bad") is False


def test_get_warnings_parses_matching_cap_alert(mocker, monkeypatch):
    rss = """<rss><channel><lastBuildDate>today</lastBuildDate>
      <item><title>Madrid: aviso naranja</title><link>https://alerts/1</link></item>
    </channel></rss>"""
    cap = """<cap:alert xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2">
      <cap:info>
        <cap:language>es-ES</cap:language>
        <cap:headline>Aviso Madrid: lluvias intensas</cap:headline>
        <cap:description>Precipitaciones fuertes</cap:description>
        <cap:onset>2026-11-16T11:00:00+00:00</cap:onset>
        <cap:expires>2026-11-16T13:00:00+00:00</cap:expires>
        <cap:parameter><cap:valueName>AEMET-Meteoalerta nivel</cap:valueName><cap:value> naranja </cap:value></cap:parameter>
        <cap:parameter><cap:valueName>AEMET-Meteoalerta probabilidad</cap:valueName><cap:value> alta </cap:value></cap:parameter>
      </cap:info>
    </cap:alert>"""
    rss_response = mocker.MagicMock(status_code=200, text=rss)
    cap_response = mocker.MagicMock(status_code=200, text=cap)
    get = mocker.MagicMock(side_effect=[rss_response, cap_response])
    monkeypatch.setattr(weather_warnings.requests, "get", get)
    monkeypatch.setattr(weather_warnings, "relative_day", lambda _value: 0)
    monkeypatch.setattr(weather_warnings, "is_alert_active", lambda _start, _end: True)

    assert weather_warnings.getWarnings("https://rss", "Madrid", timeout=3) == [{
        "title": "Aviso ",
        "description": "Precipitaciones fuertes",
        "starts": "2026-11-16T11:00:00+00:00",
        "ends": "2026-11-16T13:00:00+00:00",
        "start_offset": 0,
        "is_active": True,
        "level": " naranja ",
        "probability": " alta ",
    }]
    assert [(call.args, call.kwargs) for call in get.call_args_list] == [
        (("https://rss",), {"timeout": 3}),
        (("https://alerts/1",), {"timeout": 3}),
    ]


def test_get_warnings_returns_none_on_feed_http_or_network_failure(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=503)
    monkeypatch.setattr(weather_warnings.requests, "get", mocker.MagicMock(return_value=response))
    assert weather_warnings.getWarnings("https://rss", "Madrid") is None

    monkeypatch.setattr(weather_warnings.requests, "get", mocker.MagicMock(side_effect=requests.Timeout()))
    assert weather_warnings.getWarnings("https://rss", "Madrid") is None


def test_get_warnings_skips_nonmatching_items_and_missing_links(mocker, monkeypatch):
    rss = """<rss><channel>
      <item><title>Toledo: warning</title><link>https://alerts/outside</link></item>
      <item><title>Madrid: warning without link</title></item>
    </channel></rss>"""
    get = mocker.MagicMock(return_value=mocker.MagicMock(status_code=200, text=rss))
    monkeypatch.setattr(weather_warnings.requests, "get", get)

    assert weather_warnings.getWarnings("https://rss", "Madrid") == []
    get.assert_called_once_with("https://rss", timeout=10)


def test_get_warnings_returns_none_if_feed_has_no_channel(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200, text="<rss></rss>")
    monkeypatch.setattr(weather_warnings.requests, "get", mocker.MagicMock(return_value=response))

    assert weather_warnings.getWarnings("https://rss", "Madrid") is None
