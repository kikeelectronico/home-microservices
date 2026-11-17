import pytest

from service import BLEDelegate


def test_temperature_thermostat_packet_decodes_signed_temperature_and_humidity(mocker):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "thermostat_bathroom")

    delegate.handleNotification(1, bytes([1, 5, 149, 60]))

    assert [call.args for call in homeware.execute.call_args_list] == [
        ("thermostat_bathroom", "thermostatTemperatureAmbient", 21.5),
        ("thermostat_bathroom", "thermostatHumidityAmbient", 60),
        ("thermostat_bathroom", "online", True),
    ]


def test_temperature_sensor_packet_updates_sensor_fields(mocker):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "temperature_001")

    delegate.handleNotification(1, bytes([1, 3, 128 + 18, 128 + 45]))

    assert [call.args for call in homeware.execute.call_args_list] == [
        ("temperature_001", "temperatureAmbientCelsius", 18.3),
        ("temperature_001", "humidityAmbientPercent", 45),
        ("temperature_001", "online", True),
    ]


@pytest.mark.parametrize(
    ("battery", "description"),
    [(100, "FULL"), (75, "HIGH"), (50, "MEDIUM"), (20, "LOW"), (4, "CRITICALLY_LOW")],
)
def test_battery_packet_updates_level_and_description(mocker, battery, description):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "sensor_1")

    delegate.handleNotification(1, bytes([1, battery, 0, 0, 0]))

    homeware.execute.assert_any_call(
        "sensor_1", "capacityRemaining", [{"rawValue": battery, "unit": "PERCENTAGE"}]
    )
    homeware.execute.assert_any_call("sensor_1", "descriptiveCapacityRemaining", description)
    assert homeware.execute.call_count == 2


def test_critical_battery_logs_error(mocker, caplog):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "sensor_1")

    delegate.handleNotification(1, bytes([1, 4, 0, 0, 0]))

    assert "sensor_1: batería muy baja" in caplog.text


def test_low_battery_notification_marks_device_offline(mocker, caplog):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "sensor_1")

    delegate.handleNotification(1, bytes([7, 0, 0, 0]))

    assert [call.args for call in homeware.execute.call_args_list] == [
        ("sensor_1", "descriptiveCapacityRemaining", "LOW"),
        ("sensor_1", "online", False),
    ]
    assert "Low battery: sensor_1" in caplog.text


def test_unknown_packet_is_logged_without_homeware_updates(mocker, caplog):
    homeware = mocker.MagicMock()
    delegate = BLEDelegate(homeware, "sensor_1")

    delegate.handleNotification(1, bytes([1, 2, 3]))

    homeware.execute.assert_not_called()
    assert "Unknown package from sensor_1" in caplog.text
