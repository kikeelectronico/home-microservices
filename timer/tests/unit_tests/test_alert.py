from Alert import Alert


def test_voice_alert_publishes_to_voice_topic(mocker):
    mqtt_client = mocker.MagicMock()
    alert = Alert(mqtt_client)

    alert.voice("Prueba de voz")

    mqtt_client.publish.assert_called_once_with("notificacion/voice/alert", "Prueba de voz")


def test_message_alert_publishes_to_text_topic(mocker):
    mqtt_client = mocker.MagicMock()
    alert = Alert(mqtt_client)

    alert.message("Prueba de mensaje")

    mqtt_client.publish.assert_called_once_with("notificacion/text/alert", "Prueba de mensaje")
