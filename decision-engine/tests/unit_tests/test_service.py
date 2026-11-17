import pytest

import service


@pytest.fixture
def decision_service(mocker):
    settings = mocker.MagicMock(
        priority="high",
        homeware_api_url="https://homeware.test",
        homeware_api_key="test-key",
    )
    result = service.DecisionEngineService(settings)
    result.initialize(mocker.MagicMock())
    return result


@pytest.mark.parametrize(
    ("priority", "selected_registry"),
    [("high", "high_priority_handlers"), ("low", "low_priority_handlers"), ("unknown", "low_priority_handlers")],
)
def test_message_dispatches_event_to_handlers_for_configured_priority(
    decision_service, mocker, monkeypatch, priority, selected_registry
):
    decision_service.settings.priority = priority
    event = {"type": "device_param_update", "device_id": "lamp-1", "param": "on", "value": True}
    monkeypatch.setattr(service, "mqtt_to_event", mocker.MagicMock(return_value=event))
    handlers = [mocker.MagicMock()]
    registry = mocker.patch.object(service, selected_registry, return_value=handlers)
    context = mocker.MagicMock()
    mocker.patch.object(service, "Context", return_value=context)
    engine = mocker.MagicMock()
    engine.handle.return_value = [{"type": "notification_voice_alert", "text": "Light changed"}]
    engine_factory = mocker.patch.object(service, "Engine", return_value=engine)
    publish = mocker.patch.object(service, "publish_actions")
    payload = b"true"

    decision_service._handle_message("device/lamp-1/on", payload)

    service.mqtt_to_event.assert_called_once_with("device/lamp-1/on", "true")
    registry.assert_called_once_with()
    engine_factory.assert_called_once_with(handlers=handlers)
    engine.handle.assert_called_once()
    engine.handle.assert_called_once_with(event, context)
    publish.assert_called_once_with(engine.handle.return_value, decision_service.mqtt_client)


def test_message_with_no_event_is_ignored(decision_service, mocker, monkeypatch):
    monkeypatch.setattr(service, "mqtt_to_event", mocker.MagicMock(return_value=None))
    engine_factory = mocker.patch.object(service, "Engine")
    publish = mocker.patch.object(service, "publish_actions")

    decision_service._handle_message("unknown/topic", b"ignored")

    engine_factory.assert_not_called()
    publish.assert_not_called()
