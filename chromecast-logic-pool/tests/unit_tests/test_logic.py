import pytest

import logic


@pytest.fixture(autouse=True)
def disable_sleep(monkeypatch):
    monkeypatch.setattr(logic.time, "sleep", lambda _seconds: None)


def test_playing_lights_dims_occupied_room_and_turns_off_other_lights(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [True, "OCCUPIED", True, 42]
    previous_status = {}

    result = logic.playing_lights(homeware, False, previous_status)

    assert result is True
    assert previous_status == {"hue_17": {"brightness": 42}}
    assert homeware.execute.call_args_list == [
        mocker.call("hue_17", "brightness", 20),
        mocker.call("hue_1", "on", False),
        mocker.call("hue_9", "on", False),
        mocker.call("hue_10", "on", False),
    ]


@pytest.mark.parametrize(
    "get_values",
    [[False], [True, "UNOCCUPIED"], [True, "OCCUPIED", False]],
)
def test_playing_lights_skips_hue_17_when_scene_conditions_fail(mocker, get_values):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = get_values

    result = logic.playing_lights(homeware, False, {})

    assert result is True
    homeware.execute.assert_has_calls(
        [
            mocker.call("hue_1", "on", False),
            mocker.call("hue_9", "on", False),
            mocker.call("hue_10", "on", False),
        ]
    )
    assert homeware.execute.call_count == 3


def test_playing_lights_does_not_repeat_actions_if_already_playing(mocker):
    homeware = mocker.MagicMock()

    assert logic.playing_lights(homeware, True, {}) is True
    homeware.get.assert_not_called()
    homeware.execute.assert_not_called()


def test_not_playing_restores_saved_brightness_when_light_is_on(mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = True
    previous_status = {"hue_17": {"brightness": 42}}

    result = logic.not_playing_lights(homeware, True, previous_status)

    assert result is False
    homeware.get.assert_called_once_with("hue_17", "on")
    homeware.execute.assert_called_once_with("hue_17", "brightness", 42)


def test_not_playing_does_not_restore_brightness_when_light_is_off(mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = False
    previous_status = {"hue_17": {"brightness": 42}}

    assert logic.not_playing_lights(homeware, True, previous_status) is False
    homeware.execute.assert_not_called()


def test_not_playing_is_noop_if_not_previously_playing(mocker):
    homeware = mocker.MagicMock()

    assert logic.not_playing_lights(homeware, False, {}) is False
    homeware.get.assert_not_called()
    homeware.execute.assert_not_called()
