import pytest

import settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    settings.Settings._settings.clear()
    yield
    settings.Settings._settings.clear()


def test_loads_environment_and_integer_port(monkeypatch):
    monkeypatch.setattr(settings.os, "environ", {
        "ENV": "test",
        "MQTT_HOST": "broker",
        "MQTT_PORT": "1883",
        "MQTT_USER": "user",
        "MQTT_PASS": "password",
        "HUE_HOST": "bridge.local",
        "HUE_TOKEN": "token",
    })

    config = settings.Settings()
    config.load_settings()

    assert config.env == "test"
    assert config.service_id == "hue-outbound-test"
    assert config.mqtt_port == 1883
    assert config.hue_host == "bridge.local"


def test_missing_required_environment_variables_exit(monkeypatch):
    monkeypatch.setattr(settings.os, "environ", {"ENV": "test"})
    wait_timeouts = []
    monkeypatch.setattr(settings, "wait_for_stop", wait_timeouts.append)

    with pytest.raises(SystemExit) as exit_error:
        settings.Settings().load_settings()

    assert exit_error.value.code == 1
    assert wait_timeouts == [30]
