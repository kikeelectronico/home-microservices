import pytest

import settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings.Settings._settings.clear()
    yield
    settings.Settings._settings.clear()


def test_loads_required_and_optional_response_topics(monkeypatch):
    monkeypatch.setattr(settings.os, "environ", {
        "ENV": "test",
        "MQTT_HOST": "broker",
        "MQTT_PORT": "1883",
        "MQTT_USER": "user",
        "MQTT_PASS": "password",
        "RESPONSE_DDBB": "project.dataset.measurements",
        "RESPONSE_TEST_TRIGGER_TOPIC": "custom/trigger",
    })

    config = settings.Settings()
    config.load_settings()

    assert config.service_id == "monitor-response-test"
    assert config.mqtt_port == 1883
    assert config.response_ddbb == "project.dataset.measurements"
    assert config.response_test_trigger_topic == "custom/trigger"
    assert config.response_test_response_topic == settings.OPTIONAL_ENV_VARS["RESPONSE_TEST_RESPONSE_TOPIC"]
