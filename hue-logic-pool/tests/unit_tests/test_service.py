import json

import pytest

import service


@pytest.fixture
def logic_service(mocker):
    return service.HueLogicPoolService(mocker.MagicMock(), mocker.MagicMock())


def test_message_dispatches_button_event_and_tracks_preloaded_state(logic_service, monkeypatch, mocker):
    handler = mocker.MagicMock()
    monkeypatch.setitem(service.BUTTON_HANDLERS, "button-id", handler)
    event_service = {"id": "button-id", "button": {"last_event": "initial_press"}}

    logic_service._handle_message(json.dumps([{"data": [event_service]}]))

    handler.assert_called_once_with(
        logic_service.homeware, event_service, logic_service.buttons_preloaded_data
    )


def test_message_dispatches_dimmer_event(logic_service, monkeypatch, mocker):
    handler = mocker.MagicMock()
    monkeypatch.setitem(service.DIMMER_HANDLERS, "dimmer-id", handler)
    event_service = {"id": "dimmer-id", "relative_rotary": {"action": "start"}}

    logic_service._handle_message(json.dumps([{"data": [event_service]}]))

    handler.assert_called_once_with(
        logic_service.homeware, event_service, logic_service.dimmers_preloaded_data
    )


@pytest.mark.parametrize("message", ["not-json", "{}", '{"data": "invalid"}', '[{"data": [null]}]'])
def test_message_logs_and_ignores_invalid_payload_shapes(logic_service, message, caplog):
    logic_service._handle_message(message)

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)


def test_unknown_hue_resource_is_ignored(logic_service):
    logic_service._handle_service({"id": "unknown"})

    logic_service.homeware.execute.assert_not_called()


def test_listen_for_events_closes_stream_and_waits_before_reconnect(logic_service, monkeypatch, mocker):
    message = mocker.MagicMock(data='[{"data": []}]')
    stream = mocker.MagicMock()
    stream.events.return_value = [message]
    logic_service.hue.getEventStreamClient.return_value = stream
    stop_requested = mocker.MagicMock(side_effect=[False, False, False, False, True])
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(service, "stop_requested", stop_requested)
    monkeypatch.setattr(service, "wait_for_stop", wait_for_stop)

    logic_service._listen_for_events()

    assert logic_service.hue.getEventStreamClient.call_count == 1
    stream.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(5)
