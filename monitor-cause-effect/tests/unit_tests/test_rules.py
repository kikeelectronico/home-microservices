import pytest

import rules


@pytest.mark.parametrize(
    ("current", "operator", "expected"),
    [(4, "==", False), (5, "==", True), (6, ">", True), (5, ">", False)],
)
def test_evaluate_effect_comparison_operators(current, operator, expected):
    assert rules.evaluate_effect(current, operator, 5) is expected


def make_rule():
    return {
        "device_id": "switch-1",
        "param": "on",
        "value": True,
        "reset_value": False,
        "effects": [{
            "device_id": "lamp-1",
            "param": "on",
            "operator": "==",
            "value": True,
        }],
    }


def test_rule_sets_cause_after_two_consecutive_failed_effect_checks(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [True, False, True, False]
    mqtt_client = mocker.MagicMock()
    asserted_state = {}
    rule = make_rule()

    rules.evaluate_rule(homeware, mqtt_client, rule, asserted_state)
    assert asserted_state == {"switch-1/on/True": 1}
    mqtt_client.publish.assert_not_called()

    rules.evaluate_rule(homeware, mqtt_client, rule, asserted_state)

    assert asserted_state == {"switch-1/on/True": 2}
    mqtt_client.publish.assert_called_once_with("cause-effect/switch-1/on/True", "set")


def test_rule_resets_assertion_when_effect_recovers(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [True, True]
    mqtt_client = mocker.MagicMock()
    asserted_state = {"switch-1/on/True": 2}

    rules.evaluate_rule(homeware, mqtt_client, make_rule(), asserted_state)

    assert asserted_state == {"switch-1/on/True": 0}
    mqtt_client.publish.assert_called_once_with("cause-effect/switch-1/on/True", "reset")


def test_rule_resets_when_source_reaches_reset_value(mocker):
    homeware = mocker.MagicMock(return_value=False)
    homeware.get.side_effect = [False]
    mqtt_client = mocker.MagicMock()
    asserted_state = {"switch-1/on/True": 2}

    rules.evaluate_rule(homeware, mqtt_client, make_rule(), asserted_state)

    assert asserted_state == {"switch-1/on/True": 0}
    mqtt_client.publish.assert_called_once_with("cause-effect/switch-1/on/True", "reset")
    homeware.get.assert_called_once_with("switch-1", "on")


@pytest.mark.parametrize("state", [None, 0, 1, 2])
def test_failed_effect_advances_only_pending_states(state, mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [True, False]
    mqtt_client = mocker.MagicMock()
    asserted_state = {} if state is None else {"switch-1/on/True": state}

    rules.evaluate_rule(homeware, mqtt_client, make_rule(), asserted_state)

    if state in (None, 0):
        assert asserted_state["switch-1/on/True"] == 1
        mqtt_client.publish.assert_not_called()
    elif state == 1:
        assert asserted_state["switch-1/on/True"] == 2
        mqtt_client.publish.assert_called_once_with("cause-effect/switch-1/on/True", "set")
    else:
        assert asserted_state["switch-1/on/True"] == 2
        mqtt_client.publish.assert_not_called()


def test_evaluate_rules_processes_each_rule(mocker):
    homeware = mocker.MagicMock()
    homeware.get.side_effect = [True, False, True, False]
    mqtt_client = mocker.MagicMock()
    rules_to_evaluate = [make_rule(), {**make_rule(), "device_id": "switch-2"}]
    asserted_state = {}

    rules.evaluate_rules(homeware, mqtt_client, rules_to_evaluate, asserted_state)

    assert asserted_state == {"switch-1/on/True": 1, "switch-2/on/True": 1}
    assert homeware.get.call_count == 4
