import json
import pytest

import support

support.add_service_to_path()

import service


@pytest.fixture
def inbound_service(mocker):
    return service.HueInboundService(mocker.MagicMock(), mocker.MagicMock())


def test_initialize_builds_resource_to_device_map_and_loads_initial_values(inbound_service, monkeypatch, mocker):
    inbound_service.hue.getServices.return_value = [
        {"id": "device-1", "services": [{"rid": "motion-1"}, {"rid": "power-1"}]},
        {"id": "device-2", "services": [{"rid": "motion-2"}]},
    ]
    initializers = {
        name: mocker.MagicMock()
        for name in ("contact", "motion", "connectivity", "power", "lightlevel")
    }
    for name, initializer in initializers.items():
        monkeypatch.setattr(service.init, name, initializer)

    inbound_service.initialize()

    assert inbound_service.device_id_service_id == {
        "motion-1": "device-1",
        "power-1": "device-1",
        "motion-2": "device-2",
    }
    for initializer in initializers.values():
        initializer.assert_called_once_with(
            inbound_service.hue,
            inbound_service.homeware,
            inbound_service.device_id_service_id,
        )


def test_message_dispatches_supported_service_types(inbound_service, monkeypatch, mocker):
    handler = mocker.MagicMock()
    monkeypatch.setitem(service.SERVICE_HANDLERS, "motion", handler)
    payload = {"type": "motion", "id": "motion-1"}

    inbound_service._handle_message(json.dumps([{"data": [payload]}]))

    handler.assert_called_once_with(
        inbound_service.homeware,
        payload,
        inbound_service.device_id_service_id,
    )


def test_message_logs_and_ignores_invalid_payloads(inbound_service, caplog):
    inbound_service._handle_message("not-json")
    inbound_service._handle_message("{}")
    inbound_service._handle_message('[{"data": "not-a-list"}]')
    inbound_service._handle_message('[{"data": [null]}]')

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)


def test_unknown_service_type_is_ignored(inbound_service):
    inbound_service._handle_service({"type": "not-supported"})
