import pytest

import dimmers


def test_mirror_on_off_short_release_uses_preloaded_state(mocker):
    homeware = mocker.MagicMock()
    preloaded = {"hue_sensor_2/on": False}

    dimmers.mirror_on_off(homeware, {"button": {"last_event": "short_release"}}, preloaded)

    homeware.execute.assert_called_once_with("hue_sensor_2", "on", False)


@pytest.mark.parametrize(
    ("handler", "key", "starting_value", "expected"),
    [
        (dimmers.mirror_brightness_up, "hue_2/brightness", 70, 80),
        (dimmers.mirror_brightness_up, "hue_2/brightness", 95, 100),
        (dimmers.mirror_brightness_down, "hue_2/brightness", 30, 20),
        (dimmers.mirror_brightness_down, "hue_2/brightness", 5, 0),
    ],
)
def test_brightness_dimmers_adjust_and_clamp(handler, key, starting_value, expected, mocker):
    homeware = mocker.MagicMock()

    handler(homeware, {"button": {"last_event": "short_release"}}, {key: starting_value})

    assert [(call.args[0], call.args[1], call.args[2]) for call in homeware.execute.call_args_list] == [
        ("hue_2", "brightness", expected),
        ("hue_3", "brightness", expected),
    ]


@pytest.mark.parametrize(
    ("temperature", "expected"),
    [(2700, 5000), (5000, 2700), (3500, 2700)],
)
def test_color_temperature_dimmer_cycles_supported_values(temperature, expected, mocker):
    homeware = mocker.MagicMock()

    dimmers.mirror_color_temperature(
        homeware,
        {"button": {"last_event": "short_release"}},
        {"hue_2/color": temperature},
    )

    assert [(call.args[0], call.args[1], call.args[2]) for call in homeware.execute.call_args_list] == [
        ("hue_2", "color", {"temperatureK": expected}),
        ("hue_3", "color", {"temperatureK": expected}),
    ]


def test_initial_press_preloads_brightness_and_temperature(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [45, {"temperatureK": 2700}]
    brightness = {}
    color = {}

    dimmers.mirror_brightness_up(homeware, {"button": {"last_event": "initial_press"}}, brightness)
    dimmers.mirror_color_temperature(homeware, {"button": {"last_event": "initial_press"}}, color)

    assert brightness == {"hue_2/brightness": 45}
    assert color == {"hue_2/color": 2700}
    assert homeware.get.call_count == 2
