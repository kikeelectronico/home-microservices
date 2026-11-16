import pytest

import buttons


@pytest.mark.parametrize(
    ("handler", "device_id", "stored_key"),
    [
        (buttons.bedroom, "hue_sensor_12", "hue_sensor_12/on"),
        (buttons.kitchen, "light004", "light004/on"),
        (buttons.bathroom, "hue_sensor_14", "hue_sensor_14/on"),
    ],
)
def test_initial_press_preloads_inverse_state(handler, device_id, stored_key, mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = False
    preloaded = {}

    handler(homeware, {"button": {"last_event": "initial_press"}}, preloaded)

    assert preloaded == {stored_key: True}
    homeware.get.assert_called_once_with(device_id, "on")
    homeware.execute.assert_not_called()


@pytest.mark.parametrize(
    ("handler", "device_id", "stored_key"),
    [
        (buttons.bedroom, "hue_sensor_12", "hue_sensor_12/on"),
        (buttons.kitchen, "light004", "light004/on"),
        (buttons.bathroom, "hue_sensor_14", "hue_sensor_14/on"),
    ],
)
def test_short_release_executes_preloaded_state(handler, device_id, stored_key, mocker):
    homeware = mocker.MagicMock()
    preloaded = {stored_key: True}

    handler(homeware, {"button": {"last_event": "short_release"}}, preloaded)

    homeware.execute.assert_called_once_with(device_id, "on", True)


@pytest.mark.parametrize(
    ("handler", "device_id"),
    [
        (buttons.bedroom, "scene_dim"),
        (buttons.kitchen, "hue_17"),
        (buttons.bathroom, "hallway_switch"),
    ],
)
def test_long_press_toggles_assigned_device(handler, device_id, mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = True

    handler(homeware, {"button": {"last_event": "long_press"}}, {})

    homeware.execute.assert_called_once_with(device_id, "enable" if device_id == "scene_dim" else "on", False)


def test_unrecognized_button_event_does_not_change_state(mocker):
    homeware = mocker.MagicMock()
    preloaded = {}

    buttons.bedroom(homeware, {"button": {"last_event": "repeat"}}, preloaded)

    homeware.get.assert_not_called()
    homeware.execute.assert_not_called()
    assert preloaded == {}
