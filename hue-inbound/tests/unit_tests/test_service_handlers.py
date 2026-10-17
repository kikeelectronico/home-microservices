import pytest

import support

support.add_service_to_path()

import service_handlers


@pytest.fixture
def homeware_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def device_ids():
    return {"service-1": "device-1"}


def test_contact_and_motion_are_translated(homeware_client, device_ids):
    service_handlers.contact(homeware_client, {"id": "service-1", "contact_report": {"state": "contact"}}, device_ids)
    service_handlers.contact(homeware_client, {"id": "service-1", "contact_report": {"state": "no_contact"}}, device_ids)
    service_handlers.motion(homeware_client, {"id": "service-1", "motion": {"motion": True}}, device_ids)
    service_handlers.motion(homeware_client, {"id": "service-1", "motion": {"motion": False}}, device_ids)

    assert [(item.args, item.kwargs) for item in homeware_client.execute.call_args_list] == [
        (("device-1", "openPercent", 0), {}),
        (("device-1", "openPercent", 100), {}),
        (("device-1", "occupancy", "OCCUPIED"), {}),
        (("device-1", "occupancy", "UNOCCUPIED"), {}),
    ]


def test_connectivity_updates_current_and_legacy_device_ids(homeware_client, device_ids):
    service_handlers.connectivity(
        homeware_client,
        {"id": "service-1", "id_v1": "/sensors/sensor-7", "status": "connected"},
        device_ids,
    )

    assert [(item.args, item.kwargs) for item in homeware_client.execute.call_args_list] == [
        (("hue_sensor-7", "online", True), {}),
        (("hue_sensor_sensor-7", "online", True), {}),
        (("device-1", "online", True), {}),
    ]


@pytest.mark.parametrize(
    ("level", "description"),
    [(100, "FULL"), (70, "HIGH"), (40, "MEDIUM"), (10, "LOW"), (9, "CRITICALLY_LOW")],
)
def test_power_maps_battery_thresholds_and_legacy_device(homeware_client, device_ids, level, description):
    service_handlers.power(
        homeware_client,
        {"id": "service-1", "id_v1": "/sensors/sensor-7", "power_state": {"battery_level": level}},
        device_ids,
    )

    assert [(item.args, item.kwargs) for item in homeware_client.execute.call_args_list] == [
        (("hue_sensor_sensor-7", "descriptiveCapacityRemaining", description), {}),
        (("hue_sensor_sensor-7", "capacityRemaining", [{"rawValue": level, "unit": "PERCENTAGE"}]), {}),
        (("device-1", "descriptiveCapacityRemaining", description), {}),
        (("device-1", "capacityRemaining", [{"rawValue": level, "unit": "PERCENTAGE"}]), {}),
    ]


def test_light_level_scales_and_rounds_brightness(homeware_client, device_ids):
    service_handlers.lightlevel(homeware_client, {"id": "service-1", "light": {"light_level": 22000}}, device_ids)

    homeware_client.execute.assert_called_once_with("device-1", "brightness", 50)


def test_light_only_publishes_changed_values(homeware_client, device_ids):
    homeware_client.get.side_effect = [False, 5, {"temperatureK": 3000}]

    service_handlers.light(
        homeware_client,
        {
            "id_v1": "/lights/lamp-1",
            "on": {"on": True},
            "dimming": {"brightness": 5.4},
            "color_temperature": {"mirek": 250},
        },
        device_ids,
    )

    assert [(item.args, item.kwargs) for item in homeware_client.execute.call_args_list] == [
        (("hue_lamp-1", "on", True), {}),
        (("hue_lamp-1", "color", {"temperatureK": 4000}), {}),
    ]
