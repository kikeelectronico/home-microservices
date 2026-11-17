import json

import pytest

from infrastructure.outbound.mqtt_publisher import action_to_mqtt_message, publish_actions


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (
            {"type": "device_param_update", "device_id": "lamp-1", "param": "on", "value": True},
            ("device/control", {"id": "lamp-1", "param": "on", "value": True, "intent": "execute"}),
        ),
        (
            {
                "type": "schedule_task",
                "task_id": "task-1",
                "delta": 30,
                "target": {"device_id": "lamp-1", "param": "on", "value": True},
                "asserts": [],
            },
            (
                "tasks",
                {
                    "id": "task-1",
                    "action": "set",
                    "delta": 30,
                    "target": {"device_id": "lamp-1", "param": "on", "value": True},
                    "asserts": [],
                },
            ),
        ),
        ({"type": "cancel_task", "task_id": "task-1"}, ("tasks", {"id": "task-1", "action": "delete"})),
        ({"type": "notification_voice_alert", "text": "Hello"}, ("notificacion/voice/alert", "Hello")),
        ({"type": "notification_message_alert", "text": "Hello"}, ("notificacion/text/alert", "Hello")),
    ],
)
def test_action_to_mqtt_message_maps_action_types(action, expected):
    topic, payload = action_to_mqtt_message(action)
    expected_topic, expected_payload = expected

    assert topic == expected_topic
    assert json.loads(payload) == expected_payload if isinstance(expected_payload, dict) else payload == expected_payload


def test_unknown_action_is_skipped_and_logged(caplog):
    assert action_to_mqtt_message({"type": "unknown"}) == (None, None)
    assert "Invalid action" in caplog.text


def test_publish_actions_publishes_only_supported_actions(mocker):
    mqtt_client = mocker.MagicMock()
    actions = [
        {"type": "notification_voice_alert", "text": "Hello"},
        {"type": "device_param_update", "device_id": "lamp-1", "param": "on", "value": True},
    ]

    publish_actions(actions, mqtt_client)

    assert mqtt_client.publish.call_args_list[0].args == ("notificacion/voice/alert", "Hello")
    assert mqtt_client.publish.call_args_list[1].args[0] == "device/control"
    assert json.loads(mqtt_client.publish.call_args_list[1].args[1]) == {
        "id": "lamp-1",
        "param": "on",
        "value": True,
        "intent": "execute",
    }
