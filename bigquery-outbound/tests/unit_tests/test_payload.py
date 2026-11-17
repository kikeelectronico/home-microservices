import pytest

from service import BigQueryOutboundService


@pytest.fixture
def bigquery_service():
    return BigQueryOutboundService()


@pytest.mark.parametrize(
    ("topic", "payload", "expected"),
    [
        ("heartbeats", "service-1", "service-1"),
        ("device/thermostat_1/thermostatTemperatureAmbient", "21.5", 21.5),
        ("device/temperature_001/temperatureAmbientCelsius", "18.25", 18.25),
        ("device/hue_17/brightness", "80", 80),
        (
            "device/current001/currentSensorStateData",
            "[{'name': 'power', 'rawValue': 125}]",
            [{"name": "power", "rawValue": 125}],
        ),
    ],
)
def test_typify_payload_converts_by_topic(bigquery_service, topic, payload, expected):
    assert bigquery_service._typify_payload(topic, payload) == expected


@pytest.mark.parametrize(
    ("topic", "payload", "exception"),
    [
        ("device/hue_17/brightness", "bright", ValueError),
        ("device/thermostat_1/thermostatTemperatureAmbient", "warm", ValueError),
        ("device/thermostat_1/currentSensorStateData", "not-json", ValueError),
    ],
)
def test_typify_payload_raises_for_invalid_data(bigquery_service, topic, payload, exception):
    with pytest.raises(exception):
        bigquery_service._typify_payload(topic, payload)
