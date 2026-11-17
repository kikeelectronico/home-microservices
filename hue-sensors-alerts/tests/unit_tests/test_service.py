import json

import pytest

import service


@pytest.fixture
def alerts_service(mocker):
    return service.HueSensorsAlertsService(mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock())


@pytest.mark.parametrize("event_type", ["contact", "motion"])
def test_event_dispatches_matching_handler(alerts_service, event_type, monkeypatch, mocker):
    handler = mocker.MagicMock()
    monkeypatch.setitem(service.SERVICE_HANDLERS, event_type, handler)
    event_service = {"type": event_type, "id": "resource-1"}

    alerts_service._handle_message(json.dumps([{"data": [event_service]}]))

    handler.assert_called_once_with(alerts_service.homeware, alerts_service.mqtt_client, event_service)


@pytest.mark.parametrize("message", ["invalid-json", "{}", '{"data": null}', '[{"data": [null]}]'])
def test_invalid_event_payloads_are_logged_and_ignored(alerts_service, message, caplog):
    alerts_service._handle_message(message)

    assert caplog.records
    assert all(record.levelname == "WARNING" for record in caplog.records)


def test_unknown_service_type_is_ignored(alerts_service):
    alerts_service._handle_service({"type": "temperature", "id": "resource-1"})

    alerts_service.mqtt_client.publish.assert_not_called()


def test_listen_for_events_closes_stream_and_waits_for_reconnect(alerts_service, monkeypatch, mocker):
    stream = mocker.MagicMock()
    stream.events.return_value = [mocker.MagicMock(data='[{"data": []}]')]
    alerts_service.hue.getEventStreamClient.return_value = stream
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, False, False, False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(service, "wait_for_stop", wait_for_stop)

    alerts_service._listen_for_events()

    stream.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(5)
