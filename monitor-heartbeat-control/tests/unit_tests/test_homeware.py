import json

import Homeware


def test_execute_publishes_homeware_control_payload(mocker):
    mqtt_client = mocker.MagicMock()
    homeware = Homeware.Homeware(mqtt_client, "http://homeware", "secret")

    homeware.execute("timer-dev", "online", True)

    mqtt_client.publish.assert_called_once_with(
        "device/control",
        json.dumps({"id": "timer-dev", "param": "online", "value": True, "intent": "execute"}),
    )
