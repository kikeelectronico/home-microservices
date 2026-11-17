import json

import pytest

import service
from constants import WATER_INTERVAL, WATER_REQUEST_TOPIC, WATER_TOPIC


@pytest.fixture
def inflow_service(mocker):
    instance = service.WaterInflowService()
    instance.initialize(mocker.MagicMock())
    return instance


def test_update_if_due_publishes_payload_and_updates_timestamp(inflow_service, mocker, monkeypatch):
    payload = {"level": 72.5, "last_update": "today"}
    monkeypatch.setattr(service, "getWater", mocker.MagicMock(return_value=payload))
    now = mocker.MagicMock(side_effect=[WATER_INTERVAL + 1, WATER_INTERVAL + 1.5])
    monkeypatch.setattr(service.time, "time", now)

    inflow_service.update_if_due()

    inflow_service.mqtt_client.publish.assert_called_once_with(WATER_TOPIC, json.dumps(payload))
    assert inflow_service.last_volume_payload == payload
    assert inflow_service.last_volume_timestamp == WATER_INTERVAL + 1.5


def test_update_if_due_skips_fetch_until_interval_has_passed(inflow_service, mocker, monkeypatch):
    get_water = mocker.MagicMock()
    monkeypatch.setattr(service, "getWater", get_water)
    monkeypatch.setattr(service.time, "time", lambda: WATER_INTERVAL)

    inflow_service.update_if_due()

    get_water.assert_not_called()
    inflow_service.mqtt_client.publish.assert_not_called()


def test_unchanged_payload_is_not_published_again(inflow_service, mocker, monkeypatch):
    payload = {"level": 72.5}
    inflow_service.last_volume_payload = payload
    monkeypatch.setattr(service, "getWater", mocker.MagicMock(return_value=payload.copy()))

    inflow_service._publish_volume()

    inflow_service.mqtt_client.publish.assert_not_called()


def test_force_publishes_unchanged_payload(inflow_service, mocker, monkeypatch):
    payload = {"level": 72.5}
    inflow_service.last_volume_payload = payload
    monkeypatch.setattr(service, "getWater", mocker.MagicMock(return_value=payload.copy()))

    inflow_service._publish_volume(force=True)

    inflow_service.mqtt_client.publish.assert_called_once_with(WATER_TOPIC, json.dumps(payload))


def test_failed_water_fetch_does_not_publish_or_replace_cached_value(inflow_service, mocker, monkeypatch):
    cached_payload = {"level": 70}
    inflow_service.last_volume_payload = cached_payload
    monkeypatch.setattr(service, "getWater", mocker.MagicMock(return_value=None))

    inflow_service._publish_volume()

    inflow_service.mqtt_client.publish.assert_not_called()
    assert inflow_service.last_volume_payload is cached_payload


def test_water_request_forces_a_fresh_publication(inflow_service, mocker, monkeypatch):
    payload = {"level": 72.5}
    get_water = mocker.MagicMock(return_value=payload)
    monkeypatch.setattr(service, "getWater", get_water)

    inflow_service._handle_message(WATER_REQUEST_TOPIC, b"request")

    get_water.assert_called_once_with()
    inflow_service.mqtt_client.publish.assert_called_once_with(WATER_TOPIC, json.dumps(payload))


def test_unrelated_message_does_not_fetch_or_publish(inflow_service, mocker, monkeypatch):
    get_water = mocker.MagicMock()
    monkeypatch.setattr(service, "getWater", get_water)

    inflow_service._handle_message("other/topic", b"request")

    get_water.assert_not_called()
    inflow_service.mqtt_client.publish.assert_not_called()
