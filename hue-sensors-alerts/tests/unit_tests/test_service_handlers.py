import pytest

import service_handlers


def test_contact_alerts_only_when_away_and_contact_is_open(mocker):
    homeware = mocker.MagicMock()
    mqtt_client = mocker.MagicMock()
    homeware.get.return_value = False

    service_handlers.contact(homeware, mqtt_client, {"contact_report": {"state": "no_contact"}})

    homeware.get.assert_called_once_with("switch_at_home", "on")
    mqtt_client.publish.assert_called_once_with("notificacion/text/alert", "Alerta de contacto")


@pytest.mark.parametrize(
    ("home", "event"),
    [(True, {"contact_report": {"state": "no_contact"}}), (False, {"contact_report": {"state": "contact"}}), (False, {})],
)
def test_contact_suppresses_non_alert_conditions(home, event, mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = home
    mqtt_client = mocker.MagicMock()

    service_handlers.contact(homeware, mqtt_client, event)

    mqtt_client.publish.assert_not_called()


def test_motion_alerts_only_when_away_and_motion_is_detected(mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = False
    mqtt_client = mocker.MagicMock()

    service_handlers.motion(homeware, mqtt_client, {"motion": {"motion": True}})

    mqtt_client.publish.assert_called_once_with("notificacion/text/alert", "Alerta de movimiento")


@pytest.mark.parametrize(
    ("home", "event"),
    [(True, {"motion": {"motion": True}}), (False, {"motion": {"motion": False}}), (False, {})],
)
def test_motion_suppresses_non_alert_conditions(home, event, mocker):
    homeware = mocker.MagicMock()
    homeware.get.return_value = home
    mqtt_client = mocker.MagicMock()

    service_handlers.motion(homeware, mqtt_client, event)

    mqtt_client.publish.assert_not_called()
