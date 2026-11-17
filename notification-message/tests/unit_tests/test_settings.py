import pytest

import settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings.Settings._settings.clear()
    yield
    settings.Settings._settings.clear()


def test_loads_bot_and_chat_settings(monkeypatch):
    monkeypatch.setattr(settings.os, "environ", {
        "ENV": "test",
        "MQTT_HOST": "broker",
        "MQTT_PORT": "1883",
        "MQTT_USER": "user",
        "MQTT_PASS": "password",
        "BOT_TOKEN": "bot-token",
        "ENRIQUE_CHAT_ID": "12345",
    })

    config = settings.Settings()
    config.load_settings()

    assert config.service_id == "notification-message-test"
    assert config.mqtt_port == 1883
    assert config.bot_token == "bot-token"
    assert config.enrique_chat_id == 12345
