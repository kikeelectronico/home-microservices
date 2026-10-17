import ikea


def test_event_stream_forwards_messages_and_closes_socket(mocker, monkeypatch):
    socket = mocker.MagicMock()
    socket_factory = mocker.MagicMock(return_value=socket)
    monkeypatch.setattr(ikea, "WebSocketApp", socket_factory)
    stop_requested = mocker.MagicMock(side_effect=[False, True])
    monkeypatch.setattr(ikea, "stop_requested", stop_requested)
    message_handler = mocker.MagicMock()
    client = ikea.Ikea("ikea.local", "token")

    client.run_event_stream(message_handler)

    socket_factory.assert_called_once()
    args = socket_factory.call_args
    assert args.args == ("wss://ikea.local:8443/v1",)
    assert args.kwargs["header"] == ["Authorization: Bearer token"]
    assert args.kwargs["on_error"] == client._on_error
    assert args.kwargs["on_close"] == client._on_close
    assert args.kwargs["on_open"] == client._on_open
    args.kwargs["on_message"](socket, '{"type":"event"}')
    message_handler.assert_called_once_with('{"type":"event"}')
    socket.run_forever.assert_called_once_with(sslopt={"cert_reqs": ikea.ssl.CERT_NONE})
    socket.close.assert_called_once_with()


def test_event_stream_reconnects_after_run_error(mocker, monkeypatch):
    first_socket = mocker.MagicMock()
    first_socket.run_forever.side_effect = RuntimeError("connection lost")
    second_socket = mocker.MagicMock()
    monkeypatch.setattr(ikea, "WebSocketApp", mocker.MagicMock(side_effect=[first_socket, second_socket]))
    monkeypatch.setattr(ikea, "stop_requested", mocker.MagicMock(side_effect=[False, False, False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(ikea, "wait_for_stop", wait_for_stop)

    ikea.Ikea("ikea.local", "token").run_event_stream(mocker.MagicMock())

    first_socket.close.assert_called_once_with()
    second_socket.close.assert_called_once_with()
    wait_for_stop.assert_called_once_with(ikea.WEBSOCKET_RECONNECT_DELAY)
