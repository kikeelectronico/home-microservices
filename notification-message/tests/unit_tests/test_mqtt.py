import mqtt


def test_set_mqtt_client_registers_callbacks_and_connects(mocker, monkeypatch):
    client = mocker.MagicMock()
    monkeypatch.setattr(mqtt.mqtt, "Client", mocker.MagicMock(return_value=client))
    handler = mocker.MagicMock()

    result = mqtt.set_mqtt_client(
        "broker", 1883, "user", "password", "notification-message-test",
        ["notificacion/text/alert"], handler,
    )

    assert result is client
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.user_data_set.assert_called_once_with({
        "subscriptions": ["notificacion/text/alert"],
        "message_handler": handler,
    })
    client.username_pw_set.assert_called_once_with("user", "password")
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)


def test_connect_subscribes_to_notification_topic(mocker):
    client = mocker.MagicMock()

    mqtt.on_connect(client, {"subscriptions": ["notificacion/text/alert"]}, None, 0, None)

    client.subscribe.assert_called_once_with("notificacion/text/alert", qos=1)


def test_message_callback_passes_topic_and_payload_to_handler(mocker):
    handler = mocker.MagicMock()
    message = mocker.MagicMock(topic="notificacion/text/alert", payload="Aviso".encode())

    mqtt.on_message(mocker.MagicMock(), {"message_handler": handler}, message)

    handler.assert_called_once_with("notificacion/text/alert", b"Aviso")
