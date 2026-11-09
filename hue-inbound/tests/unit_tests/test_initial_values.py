import support

support.add_service_to_path()

import init


def test_initializers_request_resource_types_and_publish_values(mocker):
    bridge = mocker.MagicMock()
    homeware_client = mocker.MagicMock()
    ids = {
        "contact-1": "device-contact",
        "motion-1": "device-motion",
        "conn-1": "device-conn",
        "power-1": "device-power",
        "level-1": "device-level",
    }
    bridge.getServices.side_effect = [
        [{"id": "contact-1", "contact_report": {"state": "contact"}}],
        [{"id": "motion-1", "motion": {"motion": True}}],
        [{"id": "conn-1", "status": "disconnected"}],
        [{"id": "power-1", "power_state": {"battery_level": 72}}],
        [{"id": "level-1", "light": {"light_level": 11000}}],
    ]

    init.contact(bridge, homeware_client, ids)
    init.motion(bridge, homeware_client, ids)
    init.connectivity(bridge, homeware_client, ids)
    init.power(bridge, homeware_client, ids)
    init.lightlevel(bridge, homeware_client, ids)

    assert [item.kwargs for item in bridge.getServices.call_args_list] == [
        {"type": "contact"},
        {"type": "motion"},
        {"type": "zigbee_connectivity"},
        {"type": "device_power"},
        {"type": "light_level"},
    ]
    assert [(item.args, item.kwargs) for item in homeware_client.execute.call_args_list] == [
        (("device-contact", "openPercent", 0), {}),
        (("device-motion", "occupancy", "OCCUPIED"), {}),
        (("device-conn", "online", False), {}),
        (("device-power", "descriptiveCapacityRemaining", "HIGH"), {}),
        (("device-power", "capacityRemaining", [{"rawValue": 72, "unit": "PERCENTAGE"}]), {}),
        (("device-level", "brightness", 25), {}),
    ]
