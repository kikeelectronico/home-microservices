import json

import pytest

import service
from constants import POWER_CONSTANT


@pytest.fixture
def bigquery_service(mocker):
    result = service.BigQueryOutboundService()
    settings = mocker.MagicMock(device_ddbb="home_states")
    client = mocker.MagicMock()
    result.initialize(settings, client)
    return result


def test_handle_message_inserts_regular_device_state(bigquery_service, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 1700000000.75)

    bigquery_service._handle_message("device/hue_17/brightness", b"80")

    bigquery_service.bigquery_client.query.assert_called_once_with(
        '\n              INSERT INTO home_states\n              (time, device_id, param, value, type)\n'
        '              VALUES (1700000000,"hue_17","brightness","80", "int");\n            '
    )
    bigquery_service.bigquery_client.query.return_value.result.assert_called_once_with()
    assert bigquery_service.last_value["device/hue_17/brightness"] == 80


def test_handle_message_converts_current_reading_using_power_constant(bigquery_service, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 1700000000)

    bigquery_service._handle_message("device/current001/brightness", b"12")

    query = bigquery_service.bigquery_client.query.call_args.args[0]
    assert f'VALUES (1700000000,"current001","current","{12 * POWER_CONSTANT}", "int");' in query
    assert bigquery_service.last_value["device/current001/brightness"] == 12


def test_handle_message_inserts_each_current_sensor_state(bigquery_service, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 1700000000)
    payload = [
        {"name": "power", "rawValue": 125},
        {"name": "voltage", "rawValue": 230.5},
    ]

    bigquery_service._handle_message(
        "device/thermostat_livingroom/currentSensorStateData", json.dumps(payload).encode()
    )

    assert bigquery_service.bigquery_client.query.call_count == 2
    queries = [call.args[0] for call in bigquery_service.bigquery_client.query.call_args_list]
    assert any('"thermostat_livingroom","power","125", "int"' in query for query in queries)
    assert any('"thermostat_livingroom","voltage","230.5", "float"' in query for query in queries)
    assert bigquery_service.bigquery_client.query.return_value.result.call_count == 2
    assert bigquery_service.last_value["device/thermostat_livingroom/currentSensorStateData"] == payload


def test_handle_message_skips_duplicate_values(bigquery_service, mocker):
    bigquery_service.last_value["device/hue_17/brightness"] = 80
    query = mocker.patch.object(bigquery_service.bigquery_client, "query")

    bigquery_service._handle_message("device/hue_17/brightness", b"80")

    query.assert_not_called()


def test_handle_message_ignores_invalid_payload(bigquery_service, caplog):
    bigquery_service._handle_message("device/hue_17/brightness", b"high")

    bigquery_service.bigquery_client.query.assert_not_called()
    assert "Invalid payload" in caplog.text


@pytest.mark.parametrize(
    "payload",
    [b'{"name": "power", "rawValue": 10}', b'[10]', b'[{"name": "power"}]'],
)
def test_handle_message_ignores_invalid_sensor_payload(bigquery_service, payload, caplog):
    bigquery_service._handle_message("device/thermostat_livingroom/currentSensorStateData", payload)

    bigquery_service.bigquery_client.query.assert_not_called()
    assert bigquery_service.last_value["device/thermostat_livingroom/currentSensorStateData"] == 0
    assert "Invalid" in caplog.text or "Missing" in caplog.text


def test_handle_message_does_not_cache_value_when_bigquery_insert_fails(bigquery_service, mocker, caplog):
    bigquery_service.bigquery_client.query.side_effect = RuntimeError("BigQuery unavailable")

    bigquery_service._handle_message("device/hue_17/brightness", b"80")

    assert "Fail to insert state into BigQuery" in caplog.text
    assert bigquery_service.last_value["device/hue_17/brightness"] == 0
