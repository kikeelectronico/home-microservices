import datetime

import pytest
import requests

import service
from constants import HEARTBEAT_TOPIC


@pytest.fixture
def controller(mocker):
    result = service.CircadianControllerService()
    result.settings = mocker.MagicMock(
        wheather_api_key="weather-key",
        wheather_query="Madrid",
        service_id="circadian-controller-test",
    )
    result.mqtt_client = mocker.MagicMock()
    result.homeware = mocker.MagicMock()
    result.solar_cycle = {"sunrise": 6.0, "sunset": 19.0}
    return result


@pytest.mark.parametrize(
    ("hour", "expected"),
    [(5.0, 2200), (6.0, 2200), (12.5, 6500), (19.0, 2200), (21.0, 2200)],
)
def test_color_temperature_follows_daylight_curve(controller, hour, expected):
    assert controller._color_temperature(hour, sunrise=6.0, sunset=19.0) == expected


def test_color_temperature_returns_minimum_for_invalid_day_length(controller):
    assert controller._color_temperature(12, sunrise=19, sunset=6) == 2200


def test_update_solar_data_converts_weatherapi_times(controller, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"astronomy": {"astro": {"sunset": "7:30 PM", "sunrise": "6:15 AM"}}}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(service.requests, "get", get)

    controller._update_solar_data()

    assert controller.solar_cycle == {"sunrise": 6.25, "sunset": 19.5}
    get.assert_called_once_with(
        "https://api.weatherapi.com/v1/astronomy.json?key=weather-key&q=Madrid", timeout=5
    )


def test_update_solar_data_preserves_previous_values_on_http_error(controller, mocker, monkeypatch, caplog):
    monkeypatch.setattr(
        service.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503))
    )

    controller._update_solar_data()

    assert controller.solar_cycle == {"sunrise": 6.0, "sunset": 19.0}
    assert "Status code: 503" in caplog.text


@pytest.mark.parametrize("network_error", [requests.ConnectionError, requests.Timeout])
def test_update_solar_data_preserves_previous_values_on_network_error(
    controller, mocker, monkeypatch, network_error, caplog
):
    monkeypatch.setattr(service.requests, "get", mocker.MagicMock(side_effect=network_error))

    controller._update_solar_data()

    assert controller.solar_cycle == {"sunrise": 6.0, "sunset": 19.0}
    assert "Fail to update weather data" in caplog.text


@pytest.mark.parametrize(
    ("emergency", "expected_ids"),
    [
        (True, ["hue_1", "hue_4", "hue_5", "hue_6", "hue_9", "hue_10", "hue_16", "hue_17"]),
        (False, ["hue_1", "hue_4", "hue_5", "hue_6", "hue_9", "hue_10", "hue_15", "hue_16", "hue_17"]),
    ],
)
def test_run_adjusts_enabled_lights_and_skips_emergency_light(
    controller, mocker, monkeypatch, emergency, expected_ids
):
    fixed_now = datetime.datetime(2024, 6, 1, 12, 30)

    class FixedDateTime:
        @staticmethod
        def now():
            return fixed_now

    monkeypatch.setattr(service.datetime, "datetime", FixedDateTime)
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    monkeypatch.setattr(service.time, "time", mocker.MagicMock(side_effect=[11, 12]))
    monkeypatch.setattr(service, "wait_for_stop", mocker.MagicMock())
    controller.homeware.get.side_effect = [True, {"emergencia": emergency}]

    controller.run()

    assert [call.args[0] for call in controller.homeware.execute.call_args_list] == expected_ids
    expected_temperature = controller._color_temperature(12.5, 6.0, 19.0)
    assert all(call.args[1:] == ("color", {"temperatureK": expected_temperature}) for call in controller.homeware.execute.call_args_list)
    controller.mqtt_client.publish.assert_called_once_with(HEARTBEAT_TOPIC, "circadian-controller-test")


def test_run_refreshes_solar_data_once_at_four_and_resets_guard_at_four_five(
    controller, mocker, monkeypatch
):
    times = iter([datetime.datetime(2024, 6, 1, 4, 0), datetime.datetime(2024, 6, 1, 4, 5)])

    class FixedDateTime:
        @staticmethod
        def now():
            return next(times)

    monkeypatch.setattr(service.datetime, "datetime", FixedDateTime)
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, False, True]))
    monkeypatch.setattr(service.time, "time", lambda: 1)
    monkeypatch.setattr(service, "wait_for_stop", mocker.MagicMock())
    controller.homeware.get.return_value = False
    update_solar = mocker.patch.object(controller, "_update_solar_data")

    controller.run()

    update_solar.assert_called_once_with()
    assert controller.just_executed is False
