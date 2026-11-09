import support

support.add_service_to_path()

import mqtt


def test_set_client_configures_callbacks_and_connection(monkeypatch, mocker):
    client = mocker.MagicMock()
    client_factory = mocker.MagicMock(return_value=client)
    monkeypatch.setattr(mqtt.mqtt, "Client", client_factory)
    handler = mocker.MagicMock()

    result = mqtt.set_mqtt_client("broker", 1883, "user", "password", "service", ["hue/#"], handler)

    assert result is client
    client.user_data_set.assert_called_once_with({"subscriptions": ["hue/#"], "message_handler": handler})
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.username_pw_set.assert_called_once_with("user", "password")
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)


def test_connect_subscribes_and_message_forwards_payload(mocker):
    client = mocker.MagicMock()
    handler = mocker.MagicMock()
    userdata = {"subscriptions": ["hue/event", "hue/state"], "message_handler": handler}

    mqtt.on_connect(client, userdata, None, 0, None)
    mqtt.on_message(client, userdata, mocker.MagicMock(topic="hue/event", payload=b"{}"))

    assert [(item.args, item.kwargs) for item in client.subscribe.call_args_list] == [
        (("hue/event",), {"qos": 1}),
        (("hue/state",), {"qos": 1}),
    ]
    handler.assert_called_once_with("hue/event", b"{}")


def test_unexpected_disconnect_retries_until_reconnect_succeeds(monkeypatch, mocker):
    client = mocker.MagicMock()
    client.reconnect.side_effect = [RuntimeError("offline"), None]
    monkeypatch.setattr(mqtt, "stop_requested", lambda: False)
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(mqtt, "wait_for_stop", wait_for_stop)

    mqtt.on_disconnect(client, {}, None, 1, None)

    assert client.reconnect.call_count == 2
    wait_for_stop.assert_called_once_with(5)
