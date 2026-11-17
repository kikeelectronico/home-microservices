import service


def test_message_decodes_utf8_and_sends_to_configured_chat(mocker):
    bot = mocker.MagicMock()
    notification = service.NotificationMessageService(bot, 12345)

    notification._handle_message("notificacion/text/alert", "Alerta de movimiento: habitación".encode("utf-8"))

    bot.send_message.assert_called_once_with(12345, "Alerta de movimiento: habitación")


def test_empty_message_is_forwarded(mocker):
    bot = mocker.MagicMock()
    notification = service.NotificationMessageService(bot, "chat-1")

    notification._handle_message("notificacion/text/alert", b"")

    bot.send_message.assert_called_once_with("chat-1", "")
