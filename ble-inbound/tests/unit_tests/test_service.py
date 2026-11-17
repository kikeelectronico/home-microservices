import pytest

import service
from constants import API_RX_CHARACTERISTIC_UUID, API_SERVICE_UUID, API_TX_CHARACTERISTIC_UUID, ONLINE_TIMEOUT


@pytest.fixture
def ble_service(mocker):
    result = service.BLEInboundService()
    result.initialize(
        mocker.MagicMock(),
        mocker.MagicMock(),
        {"thermostat_bathroom": {"mac": "AA:BB:CC:DD:EE:FF"}},
        [],
    )
    return result


def test_get_sensors_connects_reads_characteristics_and_records_update(ble_service, mocker, monkeypatch):
    peripheral = mocker.MagicMock()
    ble_api = mocker.MagicMock()
    tx_characteristic = mocker.MagicMock(valHandle=10)
    rx_characteristic = mocker.MagicMock()
    ble_api.getCharacteristics.side_effect = [[tx_characteristic], [rx_characteristic]]
    peripheral.getServiceByUUID.return_value = ble_api
    monkeypatch.setattr(service.btle, "Peripheral", mocker.MagicMock(return_value=peripheral))
    monkeypatch.setattr(service, "time", mocker.MagicMock(time=lambda: 1234))

    ble_service._get_sensors()

    service.btle.Peripheral.assert_called_once_with("AA:BB:CC:DD:EE:FF", service.btle.ADDR_TYPE_RANDOM)
    peripheral.withDelegate.assert_called_once()
    assert isinstance(peripheral.withDelegate.call_args.args[0], service.BLEDelegate)
    peripheral.getServiceByUUID.assert_called_once_with(service.btle.UUID(API_SERVICE_UUID))
    assert ble_api.getCharacteristics.call_args_list[0].args == (service.btle.UUID(API_TX_CHARACTERISTIC_UUID),)
    assert ble_api.getCharacteristics.call_args_list[1].args == (service.btle.UUID(API_RX_CHARACTERISTIC_UUID),)
    peripheral.writeCharacteristic.assert_called_once_with(11, b"\x01\x00")
    assert [call.args[0] for call in rx_characteristic.write.call_args_list] == [bytes.fromhex("570f31"), bytes.fromhex("570200")]
    assert peripheral.waitForNotifications.call_count == 2
    peripheral.disconnect.assert_called_once_with()
    assert ble_service.last_update["thermostat_bathroom"] == 1234


def test_get_sensors_marks_long_unreachable_device_offline(ble_service, mocker, monkeypatch):
    monkeypatch.setattr(
        service.btle,
        "Peripheral",
        mocker.MagicMock(side_effect=service.btle.BTLEDisconnectError("unreachable")),
    )
    ble_service.last_update["thermostat_bathroom"] = 100
    monkeypatch.setattr(service.time, "time", lambda: 100 + ONLINE_TIMEOUT + 1)
    ble_service.homeware.get.return_value = True

    ble_service._get_sensors()

    ble_service.homeware.get.assert_called_once_with("thermostat_bathroom", "online")
    ble_service.mqtt_client.publish.assert_called_once_with(
        "notificacion/text/alert", "thermostat_bathroom inaccesible"
    )
    ble_service.homeware.execute.assert_called_once_with("thermostat_bathroom", "online", False)


def test_get_sensors_does_not_mark_recently_seen_device_offline(ble_service, mocker, monkeypatch):
    monkeypatch.setattr(
        service.btle,
        "Peripheral",
        mocker.MagicMock(side_effect=service.btle.BTLEDisconnectError("unreachable")),
    )
    ble_service.last_update["thermostat_bathroom"] = 100
    monkeypatch.setattr(service.time, "time", lambda: 101)

    ble_service._get_sensors()

    ble_service.homeware.get.assert_not_called()
    ble_service.mqtt_client.publish.assert_not_called()
    ble_service.homeware.execute.assert_not_called()


@pytest.mark.parametrize(
    ("nearby_names", "is_enabled", "should_update"),
    [(["phone"], True, False), (["phone"], False, True), ([], False, False)],
)
def test_verify_presence_updates_only_changed_devices(
    ble_service, mocker, monkeypatch, nearby_names, is_enabled, should_update
):
    ble_service.ble_presence = [{"id": "phone_presence", "name": "phone"}]
    scanner = mocker.MagicMock()
    scanner.scan.return_value = [mocker.MagicMock(getValueText=mocker.MagicMock(return_value=name)) for name in nearby_names]
    monkeypatch.setattr(service.btle, "Scanner", mocker.MagicMock(return_value=scanner))
    ble_service.homeware.get.return_value = is_enabled

    ble_service._verify_presence()

    scanner.scan.assert_called_once_with(10.0)
    ble_service.homeware.get.assert_called_once_with("phone_presence", "enable")
    if should_update:
        ble_service.homeware.execute.assert_called_once_with("phone_presence", "enable", "phone" in nearby_names)
    else:
        ble_service.homeware.execute.assert_not_called()
