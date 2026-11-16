import json

import pytest

import service


@pytest.fixture
def outbound_service(mocker):
    return service.IkeaOutboundService(mocker.MagicMock())


def test_message_dispatches_on_state(outbound_service):
    outbound_service._handle_message("device/outlet-1", json.dumps({"on": True}))

    outbound_service.ikea.updateDeviceAttribute.assert_called_once_with("outlet-1", "isOn", True)


def test_message_dispatches_air_purifier_state(outbound_service):
    outbound_service._handle_message(
        "device/air-1",
        json.dumps({"currentModeSettings": {"Modo": "Manual"}, "currentFanSpeedSetting": "Media"}),
    )

    assert [(call.args[1], call.args[2]) for call in outbound_service.ikea.updateDeviceAttribute.call_args_list] == [
        ("fanMode", "on"),
        ("motorState", 30),
        ("fanMode", "on"),
    ]


@pytest.mark.parametrize("payload", ["not-json", None, "[]", '"text"', "null"])
def test_message_logs_and_ignores_invalid_payloads(outbound_service, payload, caplog):
    outbound_service._handle_message("device/outlet-1", payload)

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)
    outbound_service.ikea.updateDeviceAttribute.assert_not_called()


def test_message_ignores_state_without_handler(outbound_service):
    outbound_service._handle_message("device/outlet-1", json.dumps({"unknown": True}))

    outbound_service.ikea.updateDeviceAttribute.assert_not_called()


def test_run_waits_until_shutdown_requested(outbound_service, mocker, monkeypatch):
    stop_requested = mocker.MagicMock(side_effect=[False, False, True])
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(service, "stop_requested", stop_requested)
    monkeypatch.setattr(service, "wait_for_stop", wait_for_stop)

    outbound_service.run()

    assert wait_for_stop.call_count == 2
    wait_for_stop.assert_called_with(1)
