from engine.engine import Engine


def test_engine_aggregates_actions_from_matching_handlers_in_order(mocker):
    event = {"type": "device_param_update", "device_id": "sensor-1"}
    context = mocker.MagicMock()
    first_actions = [{"type": "first"}]
    second_actions = [{"type": "second"}, {"type": "third"}]
    first_handler = mocker.MagicMock(can_handle=mocker.MagicMock(return_value=True))
    first_handler.handle.return_value = first_actions
    ignored_handler = mocker.MagicMock(can_handle=mocker.MagicMock(return_value=False))
    matching_handler = mocker.MagicMock(can_handle=mocker.MagicMock(return_value=True))
    matching_handler.handle.return_value = second_actions

    actions = Engine([first_handler, ignored_handler, matching_handler]).handle(event, context)

    assert actions == first_actions + second_actions
    first_handler.can_handle.assert_called_once_with(event)
    first_handler.handle.assert_called_once_with(event, context)
    ignored_handler.can_handle.assert_called_once_with(event)
    ignored_handler.handle.assert_not_called()
    matching_handler.handle.assert_called_once_with(event, context)


def test_engine_returns_empty_list_when_no_handlers_match(mocker):
    handler = mocker.MagicMock(can_handle=mocker.MagicMock(return_value=False))

    assert Engine([handler]).handle({}, mocker.MagicMock()) == []
    handler.handle.assert_not_called()
