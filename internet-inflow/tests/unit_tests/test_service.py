import json

import pytest

from constants import STATUS_REQUEST_TOPIC, STATUS_TOPIC
import service


@pytest.fixture
def inflow_service(mocker):
    instance = service.InternetInflowService()
    instance.initialize(mocker.MagicMock())
    return instance


def test_first_status_is_published_and_cached(inflow_service, mocker, monkeypatch):
    status = {"connected": True}
    check = mocker.MagicMock(return_value=status)
    monkeypatch.setattr(service, "getInternetStatus", check)

    inflow_service.publish_status()

    check.assert_called_once_with()
    inflow_service.mqtt_client.publish.assert_called_once_with(STATUS_TOPIC, json.dumps(status))
    assert inflow_service.last_status == status


@pytest.mark.parametrize("status", [{"connected": True}, {"connected": False}])
def test_unchanged_status_is_not_published_again(inflow_service, mocker, monkeypatch, status):
    inflow_service.last_status = status.copy()
    monkeypatch.setattr(service, "getInternetStatus", mocker.MagicMock(return_value=status.copy()))

    inflow_service.update_if_due()

    inflow_service.mqtt_client.publish.assert_not_called()


def test_changed_status_is_published_and_replaces_cache(inflow_service, mocker, monkeypatch):
    inflow_service.last_status = {"connected": True}
    disconnected = {"connected": False}
    monkeypatch.setattr(service, "getInternetStatus", mocker.MagicMock(return_value=disconnected))

    inflow_service.publish_status()

    inflow_service.mqtt_client.publish.assert_called_once_with(STATUS_TOPIC, json.dumps(disconnected))
    assert inflow_service.last_status == disconnected


def test_status_request_forces_publication_of_unchanged_data(inflow_service, mocker, monkeypatch):
    status = {"connected": True}
    inflow_service.last_status = status.copy()
    check = mocker.MagicMock(return_value=status.copy())
    monkeypatch.setattr(service, "getInternetStatus", check)

    inflow_service._handle_message(STATUS_REQUEST_TOPIC, b"request")

    check.assert_called_once_with()
    inflow_service.mqtt_client.publish.assert_called_once_with(STATUS_TOPIC, json.dumps(status))


def test_unrelated_message_does_not_check_or_publish(inflow_service, mocker, monkeypatch):
    check = mocker.MagicMock()
    monkeypatch.setattr(service, "getInternetStatus", check)

    inflow_service._handle_message("other/topic", b"request")

    check.assert_not_called()
    inflow_service.mqtt_client.publish.assert_not_called()
