import mqtt


def test_set_mqtt_client_sets_callbacks_credentials_and_connects(mocker, monkeypatch):
    client = mocker.MagicMock()
    monkeypatch.setattr(mqtt.mqtt, "Client", mocker.MagicMock(return_value=client))

    result = mqtt.set_mqtt_client("broker", 1883, "user", "password", "heartbeat-request")

    assert result is client
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.user_data_set.assert_called_once_with({"subscriptions": [], "message_handler": None})
    client.username_pw_set.assert_called_once_with("user", "password")
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)


def test_message_callback_forwards_payload_to_handler(mocker):
    handler = mocker.MagicMock()
    message = mocker.MagicMock(topic="heartbeats/system", payload=b"are-you-there")

    mqtt.on_message(mocker.MagicMock(), {"message_handler": handler}, message)

    handler.assert_called_once_with("heartbeats/system", b"are-you-there")
