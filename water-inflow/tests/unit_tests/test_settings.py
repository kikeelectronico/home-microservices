import pytest

from constants import ENV_VARS, SERVICE_NAME
from settings import Settings
import settings as settings_module


@pytest.fixture(autouse=True)
def reset_settings():
    Settings._settings = {}


def test_load_settings_reads_required_environment_values(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    expected = {}
    for name in ENV_VARS:
        value = "1883" if name.endswith("_PORT") else "configured"
        monkeypatch.setenv(name, value)
        expected[name.lower()] = int(value) if name.endswith("_PORT") else value

    config = Settings()
    config.load_settings()

    assert config.env == "test"
    assert config.service_id == f"{SERVICE_NAME}-test"
    for name, value in expected.items():
        assert getattr(config, name) == value


def test_missing_environment_values_wait_then_exit(mocker, monkeypatch):
    monkeypatch.setenv("ENV", "test")
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    wait = mocker.patch.object(settings_module, "wait_for_stop")

    with pytest.raises(SystemExit):
        Settings().load_settings()

    wait.assert_called_once_with(30)
