from typing import List
from shared.context import Context

MIN_LIVINGROOM_DARKNESS_TRIGGER = 15

class LivingroomSofaLightHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            ((event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" and \
            event.get("param") == "brightness") or \
            (event.get("device_id") == "pressure001" and \
            event.get("param") == "occupancy"))

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  []

        if event.get("value") == "OCCUPIED":
            actions.append({
                "type": "device_param_update",
                "device_id": "hue_1",
                "param": "on",
                "value": False
            })
        else:
            light_level = event.get("value") if event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9" else context.get("c8bd20a2-69a5-4946-b6d6-3423b560ffa9", "brightness")
            occupancy = event.get("value") if event.get("device_id") == "pressure001" else context.get("pressure001", "occupancy")
            if light_level < MIN_LIVINGROOM_DARKNESS_TRIGGER and context.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_1",
                    "param": "on",
                    "value": True
                })
            elif light_level >= MIN_LIVINGROOM_DARKNESS_TRIGGER and context.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_1",
                    "param": "on",
                    "value": False
                })

        if event.get("device_id") == "pressure001":
            if event.get("value") == "OCCUPIED":
                actions.append({
                    "type": "device_param_update",
                    "device_id": "hue_1",
                    "param": "on",
                    "value": False
                })
        elif event.get("device_id") == "c8bd20a2-69a5-4946-b6d6-3423b560ffa9":
            light_level = event.get("value")
            occupancy = payload if topic == "device/pressure001/occupancy" else homeware.get("pressure001", "occupancy")
            if light_level < MIN_LIVINGROOM_DARKNESS_TRIGGER and homeware.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
                homeware.execute("hue_1", "on", True)
            elif light_level >= MIN_LIVINGROOM_DARKNESS_TRIGGER and homeware.get("scene_awake", "enable") and occupancy == "UNOCCUPIED":
                homeware.execute("hue_1", "on", False)

        return actions
