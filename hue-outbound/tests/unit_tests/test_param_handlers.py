import pytest

import param_handlers


def test_on_updates_hue_for_boolean_values(mocker):
    bridge = mocker.MagicMock()

    param_handlers.on(bridge, "light-1", True)
    param_handlers.on(bridge, "light-1", False)

    assert [(call.args, call.kwargs) for call in bridge.updateLightService.call_args_list] == [
        (("light-1", {"on": {"on": True}}), {}),
        (("light-1", {"on": {"on": False}}), {}),
    ]


@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_on_ignores_non_boolean_values(value, mocker, caplog):
    bridge = mocker.MagicMock()

    param_handlers.on(bridge, "light-1", value)

    bridge.updateLightService.assert_not_called()
    assert "Invalid on value" in caplog.text


@pytest.mark.parametrize("brightness", [0, 25, 100, 12.5])
def test_brightness_updates_valid_percentages(brightness, mocker):
    bridge = mocker.MagicMock()

    param_handlers.brightness(bridge, "light-1", brightness)

    bridge.updateLightService.assert_called_once_with(
        "light-1", {"dimming": {"brightness": brightness}}
    )


@pytest.mark.parametrize("brightness", [-1, 101, "50", None, float("nan")])
def test_brightness_ignores_invalid_values(brightness, mocker, caplog):
    bridge = mocker.MagicMock()

    param_handlers.brightness(bridge, "light-1", brightness)

    bridge.updateLightService.assert_not_called()
    assert "Invalid brightness value" in caplog.text


def test_color_converts_kelvin_to_mirek(mocker):
    bridge = mocker.MagicMock()

    param_handlers.color(bridge, "light-1", {"temperatureK": 4000})

    bridge.updateLightService.assert_called_once_with(
        "light-1", {"color_temperature": {"mirek": 250}}
    )


@pytest.mark.parametrize("value", [{}, {"temperatureK": 0}, {"temperatureK": -1}, None, "warm"])
def test_color_ignores_invalid_temperature(value, mocker, caplog):
    bridge = mocker.MagicMock()

    param_handlers.color(bridge, "light-1", value)

    bridge.updateLightService.assert_not_called()
    assert "Invalid color temperature" in caplog.text


def test_emergency_on_sets_light_and_effect(mocker):
    bridge = mocker.MagicMock()

    param_handlers.emergency(bridge, "light-1", True)

    bridge.getService.assert_not_called()
    bridge.updateLightService.assert_called_once_with(
        "light-1",
        {
            "on": {"on": True},
            "dimming": {"brightness": 100},
            "effects": {"status": "cosmos"},
            "effects_v2": {
                "action": {
                    "effect": "cosmos",
                    "parameters": {
                        "color": {"xy": {"x": 0.6845, "y": 0.3064}},
                        "speed": 0.6151,
                    },
                }
            },
            "color": {"xy": {"x": 0.6845, "y": 0.3064}},
        },
    )


@pytest.mark.parametrize("current_state", [{}, {"effects_v2": {"status": {"effect": "no_effect"}}}])
def test_emergency_off_does_nothing_if_effect_is_not_active(current_state, mocker):
    bridge = mocker.MagicMock()
    bridge.getService.return_value = current_state

    param_handlers.emergency(bridge, "light-1", False)

    bridge.getService.assert_called_once_with("light", "light-1")
    bridge.updateLightService.assert_not_called()


def test_emergency_off_restores_default_light_state(mocker):
    bridge = mocker.MagicMock()
    bridge.getService.return_value = {"effects_v2": {"status": {"effect": "candle"}}}

    param_handlers.emergency(bridge, "light-1", False)

    bridge.updateLightService.assert_called_once_with(
        "light-1",
        {
            "on": {"on": True},
            "dimming": {"brightness": 22},
            "effects": {"status": "no_effect"},
            "effects_v2": {"status": {"effect": "no_effect", "parameters": None}},
            "color_temperature": {"mirek": 455, "mirek_valid": True},
        },
    )


@pytest.mark.parametrize("value", [1, "true", None])
def test_emergency_ignores_non_boolean_values(value, mocker, caplog):
    bridge = mocker.MagicMock()

    param_handlers.emergency(bridge, "light-1", value)

    bridge.getService.assert_not_called()
    bridge.updateLightService.assert_not_called()
    assert "Invalid emergency setting" in caplog.text
