import pytest

from infrastructure.inbound.mqtt_parser import mqtt_to_event, payload_parser


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ('{"temperature": 21}', {"temperature": 21}),
        ("true", True),
        ("FALSE", False),
        ("  occupied  ", "occupied"),
        ("null", None),
    ],
)
def test_payload_parser_handles_json_booleans_and_text(payload, expected):
    assert payload_parser(payload) == expected


def test_device_topic_is_parsed_into_device_update_event():
    assert mqtt_to_event("device/lamp-1/on", "true") == {
        "type": "device_param_update",
        "device_id": "lamp-1",
        "param": "on",
        "value": True,
    }


def test_oscillation_topic_is_parsed_into_oscillation_event():
    assert mqtt_to_event("oscillation/sensor-1/value", "3.5") == {
        "type": "oscillation",
        "device_id": "sensor-1",
        "param": "value",
        "value": 3.5,
    }


@pytest.mark.parametrize(
    ("topic", "payload"),
    [("other/topic", "value"), ("device/lamp-1/on", "null"), ("oscillation/sensor-1/value", "null")],
)
def test_unknown_topics_or_null_values_are_ignored(topic, payload):
    assert mqtt_to_event(topic, payload) is None
