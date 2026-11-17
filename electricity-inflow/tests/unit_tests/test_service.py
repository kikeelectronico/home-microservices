import json
from types import SimpleNamespace

import pytest

import service
from constants import ESIOS_INTERVAL, GRID_REQUEST_TOPIC, GRID_TOPIC


@pytest.fixture
def inflow_service(mocker):
    instance = service.ElectricityInflowService(SimpleNamespace(esios_api_key="api-key"))
    instance.initialize(mocker.MagicMock())
    return instance


def test_publish_grid_uses_api_key_and_indicator_id(inflow_service, mocker, monkeypatch):
    grid = {"co2_free_generation_percentege": 45.7}
    get_indicator = mocker.MagicMock(return_value=grid)
    monkeypatch.setattr(service, "getEsiosIndicator", get_indicator)

    inflow_service._publish_grid()

    get_indicator.assert_called_once_with("api-key", 10033)
    inflow_service.mqtt_client.publish.assert_called_once_with(GRID_TOPIC, json.dumps(grid))
    assert inflow_service.last_grid_payload == grid


def test_update_if_due_fetches_after_interval(inflow_service, mocker, monkeypatch):
    result = {"co2_free_generation_percentege": 45.7}
    get_indicator = mocker.MagicMock(return_value=result)
    monkeypatch.setattr(service, "getEsiosIndicator", get_indicator)
    monkeypatch.setattr(service.time, "time", lambda: ESIOS_INTERVAL + 1)

    inflow_service.update_if_due()

    get_indicator.assert_called_once_with("api-key", 10033)
    assert inflow_service.last_grid_timestamp == ESIOS_INTERVAL + 1


def test_update_if_due_skips_before_interval(inflow_service, mocker, monkeypatch):
    get_indicator = mocker.patch.object(service, "getEsiosIndicator")
    monkeypatch.setattr(service.time, "time", lambda: ESIOS_INTERVAL)

    inflow_service.update_if_due()

    get_indicator.assert_not_called()
    inflow_service.mqtt_client.publish.assert_not_called()


def test_unchanged_grid_is_not_republished(inflow_service, mocker, monkeypatch):
    grid = {"co2_free_generation_percentege": 45.7}
    inflow_service.last_grid_payload = grid.copy()
    monkeypatch.setattr(service, "getEsiosIndicator", mocker.MagicMock(return_value=grid.copy()))

    inflow_service._publish_grid()

    inflow_service.mqtt_client.publish.assert_not_called()


def test_grid_request_forces_publication(inflow_service, mocker, monkeypatch):
    grid = {"co2_free_generation_percentege": 45.7}
    inflow_service.last_grid_payload = grid.copy()
    get_indicator = mocker.MagicMock(return_value=grid.copy())
    monkeypatch.setattr(service, "getEsiosIndicator", get_indicator)

    inflow_service._handle_message(GRID_REQUEST_TOPIC, b"request")

    get_indicator.assert_called_once_with("api-key", 10033)
    inflow_service.mqtt_client.publish.assert_called_once_with(GRID_TOPIC, json.dumps(grid))


def test_missing_indicator_data_is_not_published(inflow_service, mocker, monkeypatch):
    monkeypatch.setattr(service, "getEsiosIndicator", mocker.MagicMock(return_value=None))

    inflow_service._publish_grid(force=True)

    inflow_service.mqtt_client.publish.assert_not_called()


def test_unrelated_message_is_ignored(inflow_service, mocker, monkeypatch):
    get_indicator = mocker.patch.object(service, "getEsiosIndicator")

    inflow_service._handle_message("other/topic", b"request")

    get_indicator.assert_not_called()
