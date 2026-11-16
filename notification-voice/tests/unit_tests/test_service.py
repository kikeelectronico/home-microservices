import pytest

import service
from constants import TOPICS


@pytest.fixture
def notification(mocker):
    result = service.NotificationVoiceService()
    result.initialize(mocker.MagicMock(), mocker.MagicMock())
    return result


def test_voice_alert_is_played_when_awake_scene_is_enabled(notification):
    notification.homeware.get.return_value = True

    notification._handle_message(TOPICS[0], "Alerta de movimiento".encode("utf-8"))

    notification.homeware.get.assert_called_once_with("scene_awake", "enable")
    notification.voice.getAndPlay.assert_called_once_with("Alerta de movimiento")


def test_voice_alert_is_suppressed_when_awake_scene_is_disabled(notification):
    notification.homeware.get.return_value = False

    notification._handle_message(TOPICS[0], b"Alerta")

    notification.voice.getAndPlay.assert_not_called()


def test_direct_voice_topic_plays_message_without_homeware_check(notification):
    notification._handle_message(TOPICS[1], "Prueba de voz".encode("utf-8"))

    notification.homeware.get.assert_not_called()
    notification.voice.getAndPlay.assert_called_once_with("Prueba de voz")


def test_unknown_topic_is_ignored(notification):
    notification._handle_message("other/topic", b"ignored")

    notification.homeware.get.assert_not_called()
    notification.voice.getAndPlay.assert_not_called()


@pytest.mark.parametrize(
    ("hour", "expected"),
    [
        (0, "buenas noches. Ya estoy preparada."),
        (6, "buenas noches. Ya estoy preparada."),
        (7, "buenos días. Ya estoy preparada."),
        (14, "buenos días. Ya estoy preparada."),
        (15, "buenas tardes. Ya estoy preparada."),
        (21, "buenas tardes. Ya estoy preparada."),
        (22, "buenas noches. Ya estoy preparada."),
        (23, "buenas noches. Ya estoy preparada."),
    ],
)
def test_wakeup_message_depends_on_local_hour(notification, monkeypatch, hour, expected):
    monkeypatch.setattr(service.time, "strftime", lambda _format: f"{hour:02}")

    notification.send_wakeup_message()

    notification.voice.getAndPlay.assert_called_once_with(expected)
