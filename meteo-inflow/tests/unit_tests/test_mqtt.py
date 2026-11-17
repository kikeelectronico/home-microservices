import mqtt


def test_set_mqtt_client_registers_callbacks_credentials_and_connection(mocker, monkeypatch):
    client = mocker.MagicMock()
    factory = mocker.MagicMock(return_value=client)
    monkeypatch.setattr(mqtt.mqtt, "Client", factory)
    handler = mocker.MagicMock()
    subscriptions = ["device/#"]

    result = mqtt.set_mqtt_client("broker", 1883, "user", "password", "service", subscriptions, handler)

    assert result is client
    assert client.user_data_set.call_args.args[0] == {
        "subscriptions": subscriptions,
        "message_handler": handler,
    }
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.username_pw_set.assert_called_once_with("user", "password")
    client.reconnect_delay_set.assert_called_once_with(min_delay=1, max_delay=60)
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)


def test_connect_subscribes_and_message_callback_forwards_payload(mocker):
    client = mocker.MagicMock()
    handler = mocker.MagicMock()
    userdata = {"subscriptions": ["device/#", "heartbeats"], "message_handler": handler}
    message = mocker.MagicMock(topic="device/lamp/on", payload=b"true")

    mqtt.on_connect(client, userdata, None, 0, None)
    mqtt.on_message(client, userdata, message)

    assert [call.args for call in client.subscribe.call_args_list] == [
        ("device/#",),
        ("heartbeats",),
    ]
    assert all(call.kwargs == {"qos": 1} for call in client.subscribe.call_args_list)
    handler.assert_called_once_with("device/lamp/on", b"true")


def test_unexpected_disconnect_retries_after_reconnect_failure(mocker, monkeypatch):
    client = mocker.MagicMock()
    client.reconnect.side_effect = [RuntimeError("offline"), None]
    monkeypatch.setattr(mqtt, "stop_requested", lambda: False)
    wait = mocker.patch.object(mqtt, "wait_for_stop")

    mqtt.on_disconnect(client, {}, None, 1, None)

    assert client.reconnect.call_count == 2
    wait.assert_called_once_with(5)
