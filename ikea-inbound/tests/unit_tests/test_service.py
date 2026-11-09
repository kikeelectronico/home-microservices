import json

import pytest

import service


@pytest.fixture
def inbound_service(mocker):
    return service.IkeaInboundService(mocker.MagicMock(), mocker.MagicMock())


def test_handle_message_dispatches_known_device_type_and_processes_tasks(inbound_service, monkeypatch, mocker):
    handler = mocker.MagicMock()
    process_tasks = mocker.MagicMock()
    monkeypatch.setitem(service.DEVICE_HANDLERS, "motionSensor", handler)
    monkeypatch.setattr(service.pending_tasks, "process", process_tasks)
    data = {
        "id": "motion-1",
        "deviceType": "motionSensor",
        "attributes": {"isDetected": True},
    }

    inbound_service._handle_message(json.dumps({"data": data}))

    handler.assert_called_once_with(inbound_service.homeware, data)
    process_tasks.assert_called_once_with(inbound_service.homeware, inbound_service.tasks)


@pytest.mark.parametrize(
    "message",
    [
        "not-json",
        None,
        "[]",
        "{}",
        '{"data": []}',
        '{"data": {"deviceType": "outlet", "attributes": null}}',
    ],
)
def test_handle_message_logs_and_ignores_malformed_events(inbound_service, message, caplog, mocker):
    process_tasks = mocker.patch.object(service.pending_tasks, "process")

    inbound_service._handle_message(message)

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)
    process_tasks.assert_not_called()


def test_handle_message_ignores_events_that_only_contain_last_modified(inbound_service, monkeypatch, mocker):
    process_tasks = mocker.patch.object(service.pending_tasks, "process")
    handler = mocker.MagicMock()
    monkeypatch.setitem(service.DEVICE_HANDLERS, "motionSensor", handler)

    inbound_service._handle_message(json.dumps({
        "data": {
            "id": "motion-1",
            "deviceType": "motionSensor",
            "lastModified": "2026-10-17T12:00:00Z",
            "attributes": {"isDetected": True},
        }
    }))

    process_tasks.assert_not_called()
    handler.assert_not_called()


def test_handle_message_ignores_unknown_device_type_but_processes_pending_tasks(inbound_service, mocker):
    process_tasks = mocker.patch.object(service.pending_tasks, "process")

    inbound_service._handle_message(json.dumps({
        "data": {"id": "other", "deviceType": "unsupported", "attributes": {}}
    }))

    process_tasks.assert_called_once_with(inbound_service.homeware, inbound_service.tasks)


def test_run_passes_message_handler_to_ikea(inbound_service):
    inbound_service.run()

    inbound_service.ikea.run_event_stream.assert_called_once_with(inbound_service._handle_message)
