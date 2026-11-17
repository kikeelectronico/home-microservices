import mqtt


def test_connect_subscribes_to_heartbeat_topics(mocker):
    client = mocker.MagicMock()
    userdata = {"subscriptions": ["device/heartbeat"]}

    mqtt.on_connect(client, userdata, None, 0, None)

    client.subscribe.assert_called_once_with("device/heartbeat", qos=1)


def test_message_callback_forwards_topic_and_payload(mocker):
    handler = mocker.MagicMock()
    message = mocker.MagicMock(topic="device/heartbeat", payload=b"timer-dev")

    mqtt.on_message(mocker.MagicMock(), {"message_handler": handler}, message)

    handler.assert_called_once_with("device/heartbeat", b"timer-dev")


def test_set_mqtt_client_sets_credentials_callbacks_and_connection(mocker, monkeypatch):
    client = mocker.MagicMock()
    monkeypatch.setattr(mqtt.mqtt, "Client", mocker.MagicMock(return_value=client))

    result = mqtt.set_mqtt_client("broker", 1883, "user", "pass", "heartbeat-control", ["device/heartbeat"])

    assert result is client
    assert client.on_connect is mqtt.on_connect
    assert client.on_message is mqtt.on_message
    assert client.on_disconnect is mqtt.on_disconnect
    client.user_data_set.assert_called_once_with({
        "subscriptions": ["device/heartbeat"],
        "message_handler": None,
    })
    client.username_pw_set.assert_called_once_with("user", "pass")
    client.connect.assert_called_once_with("broker", 1883, 60, clean_start=False)
