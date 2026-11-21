import datetime

import pytest

from constants import HEARTBEAT_TOPIC
import service


@pytest.fixture
def timer(mocker):
    settings = mocker.MagicMock(service_id="timer-test", wheather_api_key="weather-key", wheather_query="Madrid")
    mqtt_client = mocker.MagicMock()
    homeware = mocker.MagicMock()
    alert = mocker.MagicMock()
    timer_service = service.TimerService(settings, mqtt_client, homeware, alert)
    # Use valid time strings so unrelated scheduled blocks can reach their assertions.
    timer_service.astro_data = {"sunrise": "99:00:00", "sunset": "99:00:00"}
    return timer_service


def test_weekday_winter_morning_sets_thermostats_and_runs_once(timer):
    today = datetime.datetime(2024, 1, 1, 8, 30, 0)  # Monday
    timer.homeware.get.side_effect = [True, False, True]

    timer._run_time_blocks(today, "08:30:00")
    timer._run_time_blocks(today, "08:30:00")

    assert [(call.args[0], call.args[1], call.args[2]) for call in timer.homeware.execute.call_args_list] == [
        ("thermostat_dormitorio", "thermostatTemperatureSetpoint", 21),
        ("thermostat_dormitorio", "thermostatMode", "heat"),
        ("thermostat_livingroom", "thermostatTemperatureSetpoint", 22),
        ("thermostat_livingroom", "thermostatMode", "heat"),
        ("thermostat_bathroom", "thermostatTemperatureSetpoint", 21),
        ("thermostat_bathroom", "thermostatMode", "heat"),
    ]


def test_weekday_reminder_requires_home_and_not_vacation(timer):
    timer.homeware.get.side_effect = [True, False]

    timer._run_time_blocks(datetime.datetime(2024, 1, 1, 8, 55), "08:55:00")

    timer.alert.voice.assert_called_once_with("5 minutos para las nueve.")


@pytest.mark.parametrize(
    ("weekday", "at_home", "vacation", "should_alert"),
    [(0, True, False, True), (5, True, False, False), (0, True, True, False), (0, False, False, False)],
)
def test_low_light_reminder_conditions(timer, weekday, at_home, vacation, should_alert):
    today = datetime.datetime(2024, 1, 1 + weekday, 10, 30)
    timer.homeware.get.side_effect = [at_home, vacation, 10, "OCCUPIED"]

    timer._run_time_blocks(today, "10:30:00")

    if should_alert:
        timer.alert.voice.assert_called_once_with("Poca luz.")
    else:
        timer.alert.voice.assert_not_called()


def test_saturday_winter_schedule_sets_thermostats(timer):
    timer.homeware.get.side_effect = [True, True, False, True]

    timer._run_time_blocks(datetime.datetime(2024, 1, 6, 10, 0), "10:00:00")  # Saturday

    assert timer.homeware.execute.call_count == 6
    timer.homeware.execute.assert_any_call("thermostat_livingroom", "thermostatTemperatureSetpoint", 22)


def test_evening_schedule_enables_dim_scene_and_updates_heating(timer):
    timer.homeware.get.return_value = True

    timer._run_time_blocks(datetime.datetime(2024, 1, 1, 22, 0), "22:00:00")

    timer.homeware.execute.assert_any_call("thermostat_dormitorio", "thermostatTemperatureSetpoint", 19)
    timer.homeware.execute.assert_any_call("thermostat_bathroom", "thermostatMode", "off")
    timer.homeware.execute.assert_any_call("scene_dim", "enable", True)


def test_sunrise_and_sunset_trigger_astro_scene(timer):
    timer.astro_data = {"sunrise": "7:30:00", "sunset": "19:15:00"}

    timer._run_time_blocks(datetime.datetime(2024, 1, 1, 7, 30), "07:30:00")
    timer.homeware.execute.assert_called_once_with("scene_astro_day", "enable", True)
    timer.just_executed = ""

    timer._run_time_blocks(datetime.datetime(2024, 1, 1, 19, 15), "19:15:00")
    timer.homeware.execute.assert_any_call("scene_astro_day", "enable", False)


def test_astro_data_converts_weatherapi_times(timer, mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"astronomy": {"astro": {"sunset": "7:15 PM", "sunrise": "6:05 AM"}}}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(service.requests, "get", get)

    timer._update_astro_data()

    assert timer.astro_data == {"sunrise": "6:05:00", "sunset": "19:15:00"}
    get.assert_called_once_with(
        "https://api.weatherapi.com/v1/astronomy.json?key=weather-key&q=Madrid",
        timeout=5,
    )


def test_astro_data_keeps_previous_values_after_http_error(timer, mocker, monkeypatch, caplog):
    timer.astro_data = {"sunrise": "6:05:00", "sunset": "19:15:00"}
    monkeypatch.setattr(service.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503)))

    timer._update_astro_data()

    assert timer.astro_data == {"sunrise": "6:05:00", "sunset": "19:15:00"}
    assert "Status code: 503" in caplog.text


def test_heartbeat_publishes_only_after_ten_seconds(timer, mocker, monkeypatch):
    now = [10]
    monkeypatch.setattr(service.time, "time", lambda: now[0])
    timer.last_heartbeat_timestamp = 1

    timer._publish_heartbeat_if_due()
    timer.mqtt_client.publish.assert_not_called()

    now[0] = 12
    timer._publish_heartbeat_if_due()
    timer.mqtt_client.publish.assert_called_once_with(HEARTBEAT_TOPIC, "timer-test")
    assert timer.last_heartbeat_timestamp == 12
