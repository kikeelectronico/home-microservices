import asyncio
import json
import sys
import types

try:
    import fastapi  # noqa: F401
except ModuleNotFoundError:
    fastapi_stub = types.ModuleType("fastapi")

    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass

        def add_middleware(self, *args, **kwargs):
            pass

        def get(self, _path):
            return lambda handler: handler

    fastapi_stub.FastAPI = FastAPI
    middleware_stub = types.ModuleType("fastapi.middleware")
    cors_stub = types.ModuleType("fastapi.middleware.cors")
    cors_stub.CORSMiddleware = type("CORSMiddleware", (), {})
    responses_stub = types.ModuleType("fastapi.responses")

    class StreamingResponse:
        def __init__(self, body_iterator, media_type=None):
            self.body_iterator = body_iterator
            self.media_type = media_type

    responses_stub.StreamingResponse = StreamingResponse
    sys.modules["fastapi"] = fastapi_stub
    sys.modules["fastapi.middleware"] = middleware_stub
    sys.modules["fastapi.middleware.cors"] = cors_stub
    sys.modules["fastapi.responses"] = responses_stub

import main


def test_root_returns_welcome_message():
    assert asyncio.run(main.root()) == {"message": "Hello, World!"}


def test_stream_requests_initial_data_and_removes_sse_queue_after_stream_ends(mocker, monkeypatch):
    queue = object()
    panel = mocker.MagicMock()
    panel.add_sse_queue.return_value = queue

    async def stream_events(_queue):
        yield f'data: {json.dumps({"type": "water-volume", "data": 42})}\n\n'

    panel.stream_events = stream_events
    monkeypatch.setattr(main, "service", panel)

    response = asyncio.run(main.stream())

    async def consume():
        return [chunk async for chunk in response.body_iterator]

    assert response.media_type == "text/event-stream"
    assert asyncio.run(consume()) == [f'data: {json.dumps({"type": "water-volume", "data": 42})}\n\n']
    panel.add_sse_queue.assert_called_once_with()
    panel.request_initial_data.assert_called_once_with()
    panel.remove_sse_queue.assert_called_once_with(queue)


def test_stream_removes_queue_even_if_stream_raises(mocker, monkeypatch):
    queue = object()
    panel = mocker.MagicMock()
    panel.add_sse_queue.return_value = queue

    async def broken_stream(_queue):
        raise RuntimeError("stream failed")
        yield "unreachable"

    panel.stream_events = broken_stream
    monkeypatch.setattr(main, "service", panel)
    response = asyncio.run(main.stream())

    async def consume():
        return [chunk async for chunk in response.body_iterator]

    try:
        asyncio.run(consume())
    except RuntimeError as error:
        assert str(error) == "stream failed"
    else:
        raise AssertionError("stream error was not propagated")

    panel.remove_sse_queue.assert_called_once_with(queue)
