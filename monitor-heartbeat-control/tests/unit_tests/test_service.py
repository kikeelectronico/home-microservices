import service
from constants import HEARTBEAT_TOPIC


def test_initialize_sets_homeware_reference():
    monitor = service.MonitorHeartbeatControlService()
    homeware = object()

    monitor.initialize(homeware)

    assert monitor.homeware is homeware
    assert monitor.devices_heartbeats == {}


def test_heartbeat_records_timestamp_and_marks_device_online(mocker, monkeypatch, caplog):
    caplog.set_level("INFO")
    monitor = service.MonitorHeartbeatControlService()
    homeware = mocker.MagicMock()
    monitor.initialize(homeware)
    monkeypatch.setattr(service.time, "time", lambda: 1234.5)

    monitor._handle_message(HEARTBEAT_TOPIC, b"timer-dev")

    assert monitor.devices_heartbeats == {"timer-dev": 1234.5}
    homeware.execute.assert_called_once_with("timer-dev", "online", True)
    assert "timer-dev: arriba" in caplog.text


def test_repeated_heartbeat_updates_timestamp_without_new_device_log(mocker, monkeypatch, caplog):
    monitor = service.MonitorHeartbeatControlService()
    homeware = mocker.MagicMock()
    monitor.initialize(homeware)
    monitor.devices_heartbeats["timer-dev"] = 100
    monkeypatch.setattr(service.time, "time", lambda: 200)

    monitor._handle_message(HEARTBEAT_TOPIC, b"timer-dev")

    assert monitor.devices_heartbeats["timer-dev"] == 200
    homeware.execute.assert_called_once_with("timer-dev", "online", True)
    assert "arriba" not in caplog.text


def test_ignores_messages_on_other_topics(mocker):
    monitor = service.MonitorHeartbeatControlService()
    homeware = mocker.MagicMock()
    monitor.initialize(homeware)

    monitor._handle_message("other/topic", b"invalid utf-8 is not decoded")

    assert monitor.devices_heartbeats == {}
    homeware.execute.assert_not_called()
