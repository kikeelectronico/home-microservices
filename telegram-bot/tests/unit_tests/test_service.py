import pytest

import service


@pytest.fixture
def telegram_service(mocker):
    result = service.TelegramBotService()
    settings = mocker.MagicMock(
        enrique_chat_id="12345",
        homeware_api_url="https://homeware.test",
        homeware_api_key="test-key",
        get_ip_endpoint="https://ip.test",
        bucket_name="videos",
    )
    bot = mocker.MagicMock()
    storage_client = mocker.MagicMock()
    result.initialize(settings, bot, storage_client)
    return result


def _message(mocker, text, user_id="12345"):
    message = mocker.MagicMock()
    message.text = text
    message.from_user.id = user_id
    return message


@pytest.mark.parametrize(
    ("command", "response"),
    [("/start", "Hi, I am Maguna"), ("/help", "I am sorry but I don't know you.")],
)
def test_welcome_commands_reply_to_user(telegram_service, mocker, command, response):
    message = _message(mocker, command)

    telegram_service._send_welcome(message)

    telegram_service.bot.reply_to.assert_called_once_with(message, response)


def test_authorized_test_command_sends_function_response(telegram_service, mocker, monkeypatch):
    test_function = mocker.MagicMock(return_value="Service is available")
    monkeypatch.setattr(service.functions, "test", test_function)

    telegram_service._send_welcome(_message(mocker, "/test"))

    test_function.assert_called_once_with()
    telegram_service.bot.send_message.assert_called_once_with(
        "12345", "Service is available", parse_mode="Markdown"
    )


@pytest.mark.parametrize(
    ("command", "function_name", "arguments", "result", "expected_message"),
    [
        (
            "/home",
            "getHomewareTest",
            ("https://homeware.test", "test-key"),
            True,
            "Corriendo",
        ),
        ("/home", "getHomewareTest", ("https://homeware.test", "test-key"), False, "Caido"),
        ("/directions", "getPublicIP", ("https://ip.test",), "203.0.113.10", "203.0.113.10"),
    ],
)
def test_authorized_status_commands_send_results(
    telegram_service, mocker, monkeypatch, command, function_name, arguments, result, expected_message
):
    handler = mocker.MagicMock(return_value=result)
    monkeypatch.setattr(service.functions, function_name, handler)

    telegram_service._send_welcome(_message(mocker, command))

    handler.assert_called_once_with(*arguments)
    telegram_service.bot.send_message.assert_called_once_with(
        "12345", expected_message, parse_mode="Markdown"
    )


def test_unknown_command_is_denied_to_non_owner(telegram_service, mocker):
    message = _message(mocker, "/unknown", user_id="999")

    telegram_service._send_welcome(message)

    telegram_service.bot.reply_to.assert_called_once_with(message, "I am sorry but I don't know you.")
    telegram_service.bot.send_message.assert_not_called()


def test_owner_youtube_message_sends_progress_and_uploaded_links(telegram_service, mocker, monkeypatch):
    download = mocker.MagicMock(return_value=["https://storage.test/video.mp4"])
    monkeypatch.setattr(service.functions, "downloadYouTubeVideo", download)
    url = "https://youtu.be/video-id"

    telegram_service._echo_message(_message(mocker, url))

    download.assert_called_once_with(url, telegram_service.storage_client, "videos")
    assert [call.args for call in telegram_service.bot.send_message.call_args_list] == [
        ("12345", "Descargando..."),
        ("12345", "Lo tenemos"),
        ("12345", "https://storage.test/video.mp4"),
    ]
    assert all(call.kwargs == {"parse_mode": "Markdown"} for call in telegram_service.bot.send_message.call_args_list)


@pytest.mark.parametrize(
    ("user_id", "text"),
    [("999", "https://youtube.com/watch?v=video-id"), ("12345", "hello")],
)
def test_echo_ignores_non_owner_or_non_youtube_messages(telegram_service, mocker, user_id, text):
    telegram_service._echo_message(_message(mocker, text, user_id=user_id))

    telegram_service.bot.send_message.assert_not_called()
