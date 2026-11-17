import pytest

import support

support.add_service_to_path()

import settings


@pytest.fixture(autouse=True)
def clear_cached_settings():
    settings.Settings._settings.clear()
    yield
    settings.Settings._settings.clear()


def test_loads_values_converts_integer_and_builds_service_id(monkeypatch):
    environment = {
        "ENV": "prod",
        "MQTT_HOST": "broker",
        "MQTT_PORT": "1883",
        "MQTT_USER": "u",
        "MQTT_PASS": "p",
        "HOMEWARE_API_URL": "http://api",
        "HOMEWARE_API_KEY": "key",
        "HUE_HOST": "bridge",
        "HUE_TOKEN": "token",
    }
    monkeypatch.setattr(settings.os, "environ", environment)
    result = settings.Settings()

    result.load_settings()

    assert result.env == "prod"
    assert result.service_id == "hue-inbound-prod"
    assert result.mqtt_port == 1883
    assert result.mqtt_host == "broker"


def test_missing_required_variables_waits_then_exits(monkeypatch):
    monkeypatch.setattr(settings.os, "environ", {"ENV": "prod"})
    wait = []
    monkeypatch.setattr(settings, "wait_for_stop", lambda seconds: wait.append(seconds))

    with pytest.raises(SystemExit) as exit_error:
        settings.Settings().load_settings()

    assert exit_error.value.code == 1
    assert wait == [30]
