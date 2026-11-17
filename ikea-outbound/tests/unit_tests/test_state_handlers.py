import pytest

import state_handlers


@pytest.mark.parametrize(
    ("mode", "expected"),
    [("Apagado", [("fanMode", "off")]), ("Automático", [("fanMode", "auto")])],
)
def test_air_purifier_translates_non_manual_modes(mode, expected, mocker):
    ikea = mocker.MagicMock()

    state_handlers.air_purifier(ikea, "air-1", {"currentModeSettings": {"Modo": mode}})

    assert [(call.args[1], call.args[2]) for call in ikea.updateDeviceAttribute.call_args_list] == expected


@pytest.mark.parametrize(("speed", "motor_state"), [("Baja", 10), ("Media", 30), ("Alta", 50)])
def test_air_purifier_translates_manual_fan_speed(speed, motor_state, mocker):
    ikea = mocker.MagicMock()

    state_handlers.air_purifier(
        ikea,
        "air-1",
        {"currentModeSettings": {"Modo": "Manual"}, "currentFanSpeedSetting": speed},
    )

    assert [(call.args[1], call.args[2]) for call in ikea.updateDeviceAttribute.call_args_list] == [
        ("fanMode", "on"),
        ("motorState", motor_state),
        ("fanMode", "on"),
    ]


@pytest.mark.parametrize("state", [{}, {"currentModeSettings": None}, {"currentModeSettings": {}}])
def test_air_purifier_ignores_invalid_mode(state, mocker, caplog):
    ikea = mocker.MagicMock()

    state_handlers.air_purifier(ikea, "air-1", state)

    ikea.updateDeviceAttribute.assert_not_called()
    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)


@pytest.mark.parametrize("value", [True, False])
def test_on_updates_ikea_boolean_attribute(value, mocker):
    ikea = mocker.MagicMock()

    state_handlers.on(ikea, "outlet-1", {"on": value})

    ikea.updateDeviceAttribute.assert_called_once_with("outlet-1", "isOn", value)


@pytest.mark.parametrize("value", [None, "on", 1])
def test_on_ignores_non_boolean_state(value, mocker, caplog):
    ikea = mocker.MagicMock()

    state_handlers.on(ikea, "outlet-1", {"on": value})

    ikea.updateDeviceAttribute.assert_not_called()
    assert "Invalid 'on' value" in caplog.text
