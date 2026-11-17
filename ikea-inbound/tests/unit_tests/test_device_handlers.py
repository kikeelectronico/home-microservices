import pytest

import device_handlers


def test_outlet_translates_state_and_power_and_clears_running_task(mocker):
    homeware = mocker.MagicMock()
    tasks = {"outlet-1-isRunning": {"old": True}}
    voltages = {}

    device_handlers.outlet(
        homeware,
        {
            "id": "outlet-1",
            "isReachable": True,
            "attributes": {"isOn": False, "currentVoltage": 230.4, "currentAmps": 1.25},
        },
        tasks,
        voltages,
    )

    assert voltages == {"outlet-1": 230.4}
    assert "outlet-1-isRunning" not in tasks
    assert [(item.args, item.kwargs) for item in homeware.execute.call_args_list] == [
        (("outlet-1", "online", True), {}),
        (("outlet-1", "on", False), {}),
        (("outlet-1", "voltage", 230.4), {}),
        (("outlet-1", "current", 1.2), {}),
        (("outlet-1", "power", 288), {}),
        (("outlet-1", "isRunning", True), {}),
    ]


def test_outlet_schedules_not_running_for_low_current(mocker, monkeypatch):
    homeware = mocker.MagicMock()
    monkeypatch.setattr(device_handlers.time, "time", lambda: 1234)
    tasks = {}

    device_handlers.outlet(
        homeware,
        {"id": "outlet-2", "attributes": {"currentVoltage": 220, "currentAmps": 0.1}},
        tasks,
        {},
    )

    assert tasks == {
        "outlet-2-isRunning": {
            "time": 1234,
            "device_id": "outlet-2",
            "param": "isRunning",
            "value": False,
        }
    }
    homeware.execute.assert_any_call("outlet-2", "power", 22)
    assert (("outlet-2", "isRunning", True), {}) not in [
        (item.args, item.kwargs) for item in homeware.execute.call_args_list
    ]


@pytest.mark.parametrize(
    ("battery", "description"),
    [(100, "FULL"), (70, "HIGH"), (40, "MEDIUM"), (10, "LOW"), (9, "CRITICALLY_LOW")],
)
def test_motion_sensor_maps_battery_and_motion(battery, description, mocker):
    homeware = mocker.MagicMock()

    device_handlers.motion_sensor(
        homeware,
        {
            "id": "motion-1",
            "isReachable": False,
            "attributes": {"batteryPercentage": battery, "isDetected": True},
        },
    )

    homeware.execute.assert_any_call("motion-1", "online", False)
    homeware.execute.assert_any_call("motion-1", "descriptiveCapacityRemaining", description)
    homeware.execute.assert_any_call(
        "motion-1", "capacityRemaining", [{"rawValue": battery, "unit": "PERCENTAGE"}]
    )
    homeware.execute.assert_any_call("motion-1", "occupancy", "OCCUPIED")


def test_air_purifier_updates_reachability_and_changed_pm25(mocker):
    homeware = mocker.MagicMock()
    sensors = [
        {"name": "PM2.5", "rawValue": 4},
        {"name": "Other", "rawValue": 10},
    ]
    homeware.get.side_effect = [False, sensors]

    device_handlers.air_purifier(
        homeware,
        {"id": "air-1", "isReachable": True, "attributes": {"currentPM25": 8}},
    )

    assert sensors[0]["rawValue"] == 8
    homeware.execute.assert_any_call("air-1", "online", True)
    homeware.execute.assert_any_call("air-1", "currentSensorStateData", sensors)


@pytest.mark.parametrize(
    ("elapsed", "lifetime", "expected", "state"),
    [(10, 100, 10, "new"), (50, 100, 50, "good"), (95, 100, 95, "replace soon"), (100, 100, 100, "replace now"), (5, 0, 0, "new")],
)
def test_air_purifier_calculates_filter_life(elapsed, lifetime, expected, state, mocker):
    homeware = mocker.MagicMock()
    sensors = [{"name": "FilterLifeTime", "rawValue": -1}]
    homeware.get.return_value = sensors

    device_handlers.air_purifier(
        homeware,
        {"id": "air-1", "attributes": {"FilterLifeTime": lifetime, "filterElapsedTime": elapsed}},
    )

    assert sensors[0] == {"name": "FilterLifeTime", "rawValue": expected, "currentSensorState": state}
    homeware.execute.assert_called_once_with("air-1", "currentSensorStateData", sensors)


def test_air_purifier_maps_fan_mode_and_motor_speed(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [{"Modo": {"Modo": "Apagado"}}, "Baja"]

    device_handlers.air_purifier(
        homeware,
        {"id": "air-1", "attributes": {"fanMode": "high", "motorState": 40}},
    )

    homeware.execute.assert_called_once_with("air-1", "currentFanSpeedSetting", "Alta")


def test_environment_sensor_ignores_unmapped_device(mocker):
    homeware = mocker.MagicMock()

    device_handlers.environment_sensor(homeware, {"id": "unknown", "attributes": {"currentTemperature": 20}})

    homeware.execute.assert_not_called()
    homeware.get.assert_not_called()


def test_environment_sensor_updates_thermostat_and_sensor_values(mocker):
    homeware = mocker.MagicMock()
    sensors = [
        {"name": "CarbonDioxideLevel", "rawValue": 400},
        {"name": "PM2.5", "rawValue": 5},
    ]
    homeware.get.return_value = sensors

    device_handlers.environment_sensor(
        homeware,
        {
            "id": "109bf470-f27b-4a3d-bfb7-6ac284bb4ed9_1",
            "isReachable": True,
            "attributes": {"isOn": False, "currentTemperature": 21.26, "currentRH": 50.6, "currentCO2": 600, "currentPM25": 12},
        },
    )

    assert [(item.args[0], item.args[1]) for item in homeware.execute.call_args_list[:4]] == [
        ("thermostat_livingroom", "online"),
        ("thermostat_livingroom", "online"),
        ("thermostat_livingroom", "thermostatTemperatureAmbient"),
        ("thermostat_livingroom", "thermostatHumidityAmbient"),
    ]
    assert homeware.execute.call_args_list[2].args[2] == 21.3
    assert homeware.execute.call_args_list[3].args[2] == 51
    assert sensors == [
        {"name": "CarbonDioxideLevel", "rawValue": 600},
        {"name": "PM2.5", "rawValue": 12},
    ]
    assert homeware.execute.call_count == 6


@pytest.mark.parametrize(
    ("detected", "expected"),
    [(True, "leak"), (False, "no leak")],
)
def test_water_leak_sensor_updates_leak_state(detected, expected, mocker):
    homeware = mocker.MagicMock()
    initial_state = "no leak" if detected else "leak"
    sensors = [{"name": "WaterLeak", "currentSensorState": initial_state}]
    homeware.get.return_value = sensors

    device_handlers.water_leak_sensor(
        homeware,
        {"id": "water-1", "isReachable": True, "attributes": {"waterLeakDetected": detected}},
    )

    assert sensors[0]["currentSensorState"] == expected
    homeware.execute.assert_any_call("water-1", "online", True)
    homeware.execute.assert_any_call("water-1", "currentSensorStateData", sensors)
