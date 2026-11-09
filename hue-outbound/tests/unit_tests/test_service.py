import json

import pytest

import service


@pytest.fixture
def outbound_service(mocker):
    return service.HueOutboundService(mocker.MagicMock())


def test_initialize_maps_legacy_device_ids_to_light_services(outbound_service):
    outbound_service.hue.getServices.return_value = [
        {
            "id_v1": "/lights/lamp-1",
            "services": [
                {"rid": "light-service-1", "rtype": "light"},
                {"rid": "motion-service-1", "rtype": "motion"},
            ],
        },
        {"id_v1": "/lights/lamp-2", "services": [{"rid": "light-service-2", "rtype": "light"}]},
        {"id": "device-without-v1", "services": [{"rid": "light-service-3", "rtype": "light"}]},
    ]

    outbound_service.initialize()

    outbound_service.hue.getServices.assert_called_once_with(type="device")
    assert outbound_service.service_id_device_id == {
        "lamp-1": "light-service-1",
        "lamp-2": "light-service-2",
    }
    assert outbound_service.topics == ["device/hue_lamp-1", "device/hue_lamp-2"]


@pytest.mark.parametrize(
    ("payload", "expected_properties"),
    [
        ({"on": True}, {"on": {"on": True}}),
        ({"brightness": 50}, {"dimming": {"brightness": 50}}),
        ({"currentToggleSettings": {"emergencia": True}}, {"effects": {"status": "cosmos"}}),
    ],
)
def test_message_routes_supported_and_nested_parameters(outbound_service, payload, expected_properties):
    outbound_service.service_id_device_id["lamp-1"] = "light-service-1"

    outbound_service._handle_message("device/hue_lamp-1", json.dumps(payload))

    outbound_service.hue.updateLightService.assert_called_once()
    assert outbound_service.hue.updateLightService.call_args.args[0] == "light-service-1"
    actual_properties = outbound_service.hue.updateLightService.call_args.args[1]
    for key, expected_value in expected_properties.items():
        assert actual_properties[key] == expected_value


@pytest.mark.parametrize("payload", [b"invalid-json", b"[]", b'"value"', b"null"])
def test_message_logs_and_ignores_invalid_payloads(outbound_service, payload, caplog):
    outbound_service._handle_message("device/hue_lamp-1", payload)

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)
    outbound_service.hue.updateLightService.assert_not_called()


def test_message_warns_when_device_has_no_hue_mapping(outbound_service, caplog):
    outbound_service._handle_message("device/hue_missing-lamp", json.dumps({"on": True}))

    assert "No hue mapping" in caplog.text
    outbound_service.hue.updateLightService.assert_not_called()


def test_message_ignores_unknown_parameter(outbound_service):
    outbound_service.service_id_device_id["lamp-1"] = "light-service-1"

    outbound_service._handle_message("device/hue_lamp-1", json.dumps({"unsupported": "value"}))

    outbound_service.hue.updateLightService.assert_not_called()


def test_run_waits_until_shutdown_is_requested(outbound_service, monkeypatch, mocker):
    stop_requested = mocker.MagicMock(side_effect=[False, False, True])
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(service, "stop_requested", stop_requested)
    monkeypatch.setattr(service, "wait_for_stop", wait_for_stop)

    outbound_service.run()

    assert wait_for_stop.call_count == 2
    wait_for_stop.assert_called_with(1)
