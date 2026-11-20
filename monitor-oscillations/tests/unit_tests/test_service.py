from constants import HEARTBEAT_TOPIC, OSCILLATION_THRESHOLD
import service


def test_first_device_message_initializes_tracking_state(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    monkeypatch.setattr(service.time, "time", lambda: 100)

    monitor._handle_message("device/lamp-1/on", b"off")

    assert monitor.last_status == {
        "lamp-1/on": {
            "timestamp": 100,
            "value": b"off",
            "counter": 0,
            "oscillating": False,
        }
    }
    mqtt_client.publish.assert_not_called()


def test_repeated_changes_within_threshold_raise_oscillation(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    now = [100]
    monkeypatch.setattr(service.time, "time", lambda: now[0])

    monitor._handle_message("device/lamp-1/on", b"off")
    now[0] = 101
    monitor._handle_message("device/lamp-1/on", b"on")
    assert monitor.last_status["lamp-1/on"]["counter"] == 1
    mqtt_client.publish.assert_not_called()

    now[0] = 102
    monitor._handle_message("device/lamp-1/on", b"off")

    assert monitor.last_status["lamp-1/on"]["oscillating"] is True
    assert monitor.last_status["lamp-1/on"]["value"] == b"off"
    mqtt_client.publish.assert_called_once_with("oscillation/lamp-1/on", "set")


def test_unchanged_value_does_not_update_timestamp_or_publish(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    now = [10]
    monkeypatch.setattr(service.time, "time", lambda: now[0])
    monitor._handle_message("device/sensor-1/temperature", b"20")
    now[0] = 12

    monitor._handle_message("device/sensor-1/temperature", b"20")

    assert monitor.last_status["sensor-1/temperature"]["timestamp"] == 10
    assert monitor.last_status["sensor-1/temperature"]["counter"] == 0
    mqtt_client.publish.assert_not_called()


def test_change_outside_threshold_starts_new_window_without_oscillation(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    now = [10]
    monkeypatch.setattr(service.time, "time", lambda: now[0])
    monitor._handle_message("device/sensor-1/on", b"off")
    now[0] = 10 + OSCILLATION_THRESHOLD

    monitor._handle_message("device/sensor-1/on", b"on")

    status = monitor.last_status["sensor-1/on"]
    assert status["timestamp"] == now[0]
    assert status["value"] == b"on"
    assert status["counter"] == 0
    assert status["oscillating"] is False
    mqtt_client.publish.assert_not_called()


def test_heartbeat_resets_oscillation_only_after_threshold(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    monitor.last_status["lamp-1/on"] = {
        "timestamp": 100,
        "value": b"on",
        "counter": 1,
        "oscillating": True,
    }
    now = [100 + OSCILLATION_THRESHOLD]
    monkeypatch.setattr(service.time, "time", lambda: now[0])

    monitor._handle_message(HEARTBEAT_TOPIC, b"heartbeat")

    mqtt_client.publish.assert_not_called()
    assert monitor.last_status["lamp-1/on"]["oscillating"] is True

    now[0] += 1
    monitor._handle_message(HEARTBEAT_TOPIC, b"heartbeat")

    assert monitor.last_status["lamp-1/on"]["counter"] == 0
    assert monitor.last_status["lamp-1/on"]["oscillating"] is False
    mqtt_client.publish.assert_called_once_with("oscillation/lamp-1/on", "reset")


def test_non_heartbeat_message_does_not_reset_oscillation(mocker, monkeypatch):
    monitor = service.MonitorOscillationsService()
    mqtt_client = mocker.MagicMock()
    monitor.initialize(mqtt_client)
    monitor.last_status["lamp-1/on"] = {
        "timestamp": 10,
        "value": b"on",
        "counter": 1,
        "oscillating": True,
    }
    monkeypatch.setattr(service.time, "time", lambda: 100)

    monitor._handle_message("device/other/on", b"off")

    assert monitor.last_status["lamp-1/on"]["oscillating"] is True
    mqtt_client.publish.assert_not_called()
