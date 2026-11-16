import service


def test_service_evaluates_rules_and_retains_state(mocker):
    homeware = mocker.MagicMock()
    mqtt_client = mocker.MagicMock()
    rules = [{
        "device_id": "switch-1",
        "param": "on",
        "value": True,
        "reset_value": False,
        "effects": [{"device_id": "lamp-1", "param": "on", "operator": "==", "value": True}],
    }]
    homeware.get.side_effect = [True, False, True, False]
    monitor = service.MonitorCauseEffectService(homeware, mqtt_client, rules)

    monitor.evaluate_rules()
    assert monitor.asserted_state == {"switch-1/on/True": 1}
    monitor.evaluate_rules()

    assert monitor.asserted_state == {"switch-1/on/True": 2}
    mqtt_client.publish.assert_called_once_with("cause-effect/switch-1/on/True", "set")
