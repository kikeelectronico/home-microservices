import main


def test_main_sends_heartbeat_until_shutdown_and_disconnects(mocker, monkeypatch):
    settings = mocker.MagicMock(env="test", service_id="monitor-heartbeat-request-test")
    monkeypatch.setattr(main, "Settings", mocker.MagicMock(return_value=settings))

    mqtt_client = mocker.MagicMock()
    set_client = mocker.MagicMock(return_value=mqtt_client)
    monkeypatch.setattr(main, "set_mqtt_client", set_client)

    heartbeat_service = mocker.MagicMock()
    service_factory = mocker.MagicMock(return_value=heartbeat_service)
    monkeypatch.setattr(main, "MonitorHeartbeatRequestService", service_factory)
    monkeypatch.setattr(main, "stop_requested", mocker.MagicMock(side_effect=[False, False, True]))
    wait_for_stop = mocker.MagicMock()
    monkeypatch.setattr(main, "wait_for_stop", wait_for_stop)
    register_shutdown_handlers = mocker.MagicMock()
    monkeypatch.setattr(main, "register_shutdown_handlers", register_shutdown_handlers)

    main.main()

    register_shutdown_handlers.assert_called_once_with()
    settings.load_settings.assert_called_once_with()
    set_client.assert_called_once_with(
        settings.mqtt_host,
        settings.mqtt_port,
        settings.mqtt_user,
        settings.mqtt_pass,
        settings.service_id,
    )
    heartbeat_service.initialize.assert_called_once_with(mqtt_client)
    assert heartbeat_service.publish_heartbeat_request.call_count == 2
    assert [(call.args, call.kwargs) for call in wait_for_stop.call_args_list] == [((10,), {}), ((10,), {})]
    mqtt_client.loop_start.assert_called_once_with()
    mqtt_client.loop_stop.assert_called_once_with()
    mqtt_client.disconnect.assert_called_once_with()
