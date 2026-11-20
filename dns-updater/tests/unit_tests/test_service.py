import pytest
import requests

from constants import HEARTBEAT_TOPIC, REQUEST_TIMEOUT, SLEEP_TIME
import service


@pytest.fixture
def dns_updater(mocker):
    settings = mocker.MagicMock(
        get_ip_endpoint="https://ip.test",
        cloudflare_zone="zone-id",
        cloudflare_dns_id="record-id",
        cloudflare_token="api-token",
        service_id="dns-updater-test",
    )
    mqtt_client = mocker.MagicMock()
    result = service.DNSUpdaterService()
    result.initialize(settings, mqtt_client)
    return result


def test_updates_cloudflare_when_public_ip_changes(dns_updater, mocker, monkeypatch):
    get = mocker.MagicMock(return_value=mocker.MagicMock(text="192.168.1.1"))
    patch = mocker.MagicMock(return_value=mocker.MagicMock(json=lambda: {"success": True}))
    monkeypatch.setattr(service.requests, "get", get)
    monkeypatch.setattr(service.requests, "request", patch)

    dns_updater._update_dns_if_needed()

    get.assert_called_once_with("https://ip.test", timeout=REQUEST_TIMEOUT)
    patch.assert_called_once_with(
        "PATCH",
        "https://api.cloudflare.com/client/v4/zones/zone-id/dns_records/record-id",
        headers={"Authorization": "Bearer api-token", "Content-Type": "application/json"},
        data='{"content": "192.168.1.1"}',
        timeout=REQUEST_TIMEOUT,
    )
    assert dns_updater.last_ip == "192.168.1.1"
    dns_updater.mqtt_client.publish.assert_not_called()


def test_does_not_update_cloudflare_when_ip_is_unchanged(dns_updater, mocker, monkeypatch):
    dns_updater.last_ip = "192.168.1.1"
    get = mocker.MagicMock(return_value=mocker.MagicMock(text="192.168.1.1"))
    patch = mocker.MagicMock()
    monkeypatch.setattr(service.requests, "get", get)
    monkeypatch.setattr(service.requests, "request", patch)

    dns_updater._update_dns_if_needed()

    get.assert_called_once_with("https://ip.test", timeout=REQUEST_TIMEOUT)
    patch.assert_not_called()


@pytest.mark.parametrize("invalid_ip", ["unknown", "203.0.113", "192.168.1.1.1"])
def test_ignores_invalid_public_ip(dns_updater, mocker, monkeypatch, invalid_ip):
    get = mocker.MagicMock(return_value=mocker.MagicMock(text=invalid_ip))
    patch = mocker.MagicMock()
    monkeypatch.setattr(service.requests, "get", get)
    monkeypatch.setattr(service.requests, "request", patch)

    dns_updater._update_dns_if_needed()

    patch.assert_not_called()
    assert dns_updater.last_ip == "unknown"


def test_notifies_when_cloudflare_rejects_update(dns_updater, mocker, monkeypatch, caplog):
    monkeypatch.setattr(
        service.requests,
        "get",
        mocker.MagicMock(return_value=mocker.MagicMock(text="192.168.1.1")),
    )
    monkeypatch.setattr(
        service.requests,
        "request",
        mocker.MagicMock(return_value=mocker.MagicMock(json=lambda: {"success": False})),
    )

    dns_updater._update_dns_if_needed()

    dns_updater.mqtt_client.publish.assert_called_once_with(
        "notificacion/text/alert", "Problemas al actualizar la IP de Homeware"
    )
    assert dns_updater.last_ip == "192.168.1.1"
    assert "Problemas al actualizar la IP de Homeware" in caplog.text


def test_run_publishes_heartbeat_and_waits(dns_updater, mocker, monkeypatch):
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    update = mocker.patch.object(dns_updater, "_update_dns_if_needed")
    wait = mocker.patch.object(service, "wait_for_stop")

    dns_updater.run()

    update.assert_called_once_with()
    dns_updater.mqtt_client.publish.assert_called_once_with(HEARTBEAT_TOPIC, "dns-updater-test")
    wait.assert_called_once_with(SLEEP_TIME)


@pytest.mark.parametrize("network_error", [requests.ConnectTimeout, requests.ConnectionError])
def test_run_handles_network_errors_and_continues_waiting(dns_updater, mocker, monkeypatch, network_error):
    monkeypatch.setattr(service, "stop_requested", mocker.MagicMock(side_effect=[False, True]))
    update = mocker.patch.object(dns_updater, "_update_dns_if_needed", side_effect=network_error)
    wait = mocker.patch.object(service, "wait_for_stop")

    dns_updater.run()

    update.assert_called_once_with()
    dns_updater.mqtt_client.publish.assert_not_called()
    wait.assert_called_once_with(SLEEP_TIME)
