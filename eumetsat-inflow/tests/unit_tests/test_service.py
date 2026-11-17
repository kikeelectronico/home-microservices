import json
from types import SimpleNamespace

import pytest

import service
from constants import NEAREST_FIRE_INTERVAL, NEAREST_FIRE_REQUEST_TOPIC, NEAREST_FIRE_TOPIC


@pytest.fixture
def inflow_service(mocker):
    settings = SimpleNamespace(
        eumetsat_consumer_key="consumer-key",
        eumetsat_consumer_secret="consumer-secret",
        reference_lat="40.4",
        reference_lon="-3.7",
        bounding_box="-6.18, 39.13, -2.67, 41.36",
    )
    instance = service.EumetsatInflowService(settings)
    instance.initialize(mocker.MagicMock())
    return instance


def test_publish_nearest_fire_uses_settings_and_publishes(inflow_service, mocker, monkeypatch):
    result = {"distance": 12.3, "latitude": 40.1, "longitud": -3.4, "frp": 50}
    get_nearest = mocker.MagicMock(return_value=result)
    monkeypatch.setattr(service, "getNearestFire", get_nearest)

    inflow_service._publish_nearest_fire()

    get_nearest.assert_called_once_with(
        consumer_key="consumer-key",
        consumer_secret="consumer-secret",
        ref_lat=40.4,
        ref_lon=-3.7,
        bbox="-6.18, 39.13, -2.67, 41.36",
    )
    inflow_service.mqtt_client.publish.assert_called_once_with(NEAREST_FIRE_TOPIC, json.dumps(result))
    assert inflow_service.last_nearest_fire_payload == result


def test_update_if_due_fetches_after_interval_and_updates_timestamp(inflow_service, mocker, monkeypatch):
    result = {"distance": 12.3}
    get_nearest = mocker.MagicMock(return_value=result)
    monkeypatch.setattr(service, "getNearestFire", get_nearest)
    monkeypatch.setattr(service.time, "time", lambda: NEAREST_FIRE_INTERVAL + 1)

    inflow_service.update_if_due()

    get_nearest.assert_called_once()
    assert inflow_service.last_nearest_fire_timestamp == NEAREST_FIRE_INTERVAL + 1
    inflow_service.mqtt_client.publish.assert_called_once_with(NEAREST_FIRE_TOPIC, json.dumps(result))


def test_update_if_due_skips_before_interval(inflow_service, mocker, monkeypatch):
    get_nearest = mocker.patch.object(service, "getNearestFire")
    monkeypatch.setattr(service.time, "time", lambda: NEAREST_FIRE_INTERVAL)

    inflow_service.update_if_due()

    get_nearest.assert_not_called()
    inflow_service.mqtt_client.publish.assert_not_called()


def test_identical_fire_payload_is_not_published_twice(inflow_service, mocker, monkeypatch):
    result = {"distance": 12.3}
    inflow_service.last_nearest_fire_payload = result.copy()
    monkeypatch.setattr(service, "getNearestFire", mocker.MagicMock(return_value=result.copy()))

    inflow_service._publish_nearest_fire()

    inflow_service.mqtt_client.publish.assert_not_called()


def test_request_topic_forces_publication_of_identical_data(inflow_service, mocker, monkeypatch):
    result = {"distance": 12.3}
    inflow_service.last_nearest_fire_payload = result.copy()
    get_nearest = mocker.MagicMock(return_value=result.copy())
    monkeypatch.setattr(service, "getNearestFire", get_nearest)

    inflow_service._handle_message(NEAREST_FIRE_REQUEST_TOPIC, b"request")

    get_nearest.assert_called_once()
    inflow_service.mqtt_client.publish.assert_called_once_with(NEAREST_FIRE_TOPIC, json.dumps(result))


def test_missing_fire_data_is_not_published(inflow_service, mocker, monkeypatch):
    monkeypatch.setattr(service, "getNearestFire", mocker.MagicMock(return_value=None))

    inflow_service._publish_nearest_fire(force=True)

    inflow_service.mqtt_client.publish.assert_not_called()


def test_unrelated_request_topic_is_ignored(inflow_service, mocker, monkeypatch):
    get_nearest = mocker.patch.object(service, "getNearestFire")

    inflow_service._handle_message("other/topic", b"request")

    get_nearest.assert_not_called()
