import asyncio
import json

import pytest

from service import DataPanelService
import service


@pytest.fixture
def panel_service():
    return DataPanelService([])


def test_add_and_remove_sse_queue(panel_service):
    queue = panel_service.add_sse_queue()
    assert queue in panel_service.sse_queues

    panel_service.remove_sse_queue(queue)
    panel_service.remove_sse_queue(queue)

    assert queue not in panel_service.sse_queues


def test_dispatch_mqtt_events_fans_out_to_all_sse_queues(panel_service, mocker, monkeypatch):
    first = panel_service.add_sse_queue()
    second = panel_service.add_sse_queue()
    event = {"type": "internet-status", "data": {"online": True}}
    panel_service.mqtt_events.put(event)
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))

    asyncio.run(panel_service.dispatch_mqtt_events())

    assert first.get_nowait() == event
    assert second.get_nowait() == event
    assert panel_service.mqtt_events.empty()


def test_dispatch_waits_when_there_are_no_events(panel_service, mocker, monkeypatch):
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    sleep = mocker.AsyncMock()
    monkeypatch.setattr(service, "sleep", sleep)

    asyncio.run(panel_service.dispatch_mqtt_events())

    sleep.assert_awaited_once_with(0.1)


def test_stream_events_emits_server_sent_event_and_finishes(panel_service, mocker, monkeypatch):
    event = {"type": "water-volume", "data": {"liters": 12}}
    queue = panel_service.add_sse_queue()
    queue.put_nowait(event)
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    monkeypatch.setattr(service, "sleep", mocker.AsyncMock())

    async def collect():
        return [item async for item in panel_service.stream_events(queue)]

    assert asyncio.run(collect()) == [f"data: {json.dumps(event)}\n\n"]


def test_stream_events_stops_without_yielding_when_shutdown_requested(panel_service, monkeypatch):
    monkeypatch.setattr(service, "stop_requested", lambda: True)

    async def collect():
        return [item async for item in panel_service.stream_events(asyncio.Queue())]

    assert asyncio.run(collect()) == []
