import mqtt


def test_set_mqtt_client_configures_and_connects_client(mocker, monkeypatch):
    client = mocker.MagicMock()
    client_factory = mocker.MagicMock(return_value=client)
    monkeypatch.setattr(mqtt.mqtt, "Client", client_factory)
    handler = mocker.MagicMock()

    result = mqtt.set_mqtt_client(
        "broker", 1883, "user", "password", "hue-outbound-test",
        ["device/hue_#"], handler,
    )

    assert result is client
    client.user_data_set.assert_called_once_with({
        "subscriptions": ["device/hue_#"],
        "message_handler": handler,
    })
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.username_pw_set.assert_called_once_with("user", "password")
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)


def test_connect_subscribes_to_configured_topics(mocker):
    client = mocker.MagicMock()

    mqtt.on_connect(client, {"subscriptions": ["device/hue_a", "device/hue_b"]}, None, 0, None)

    assert [(item.args, item.kwargs) for item in client.subscribe.call_args_list] == [
        (("device/hue_a",), {"qos": 1}),
        (("device/hue_b",), {"qos": 1}),
    ]


def test_message_forwards_to_registered_handler(mocker):
    handler = mocker.MagicMock()
    message = type("Message", (), {"topic": "device/hue_lamp-1", "payload": b'{"on":true}'})()

    mqtt.on_message(mocker.MagicMock(), {"message_handler": handler}, message)

    handler.assert_called_once_with("device/hue_lamp-1", b'{"on":true}')


def test_disconnect_retries_until_connection_is_restored(mocker, monkeypatch):
    client = mocker.MagicMock()
    client.reconnect.side_effect = [RuntimeError("offline"), None]
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(mqtt, "stop_requested", lambda: False)
    monkeypatch.setattr(mqtt, "wait_for_stop", wait_for_stop)

    mqtt.on_disconnect(client, {}, None, 1, None)

    assert client.reconnect.call_count == 2
    wait_for_stop.assert_called_once_with(5)
