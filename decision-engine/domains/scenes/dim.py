from typing import List
from shared.context import Context


class DimSceneHandler:
    def can_handle(self, event: dict) -> bool:
        return event.get("type") == "device_param_update" and \
            event.get("device_id") == "scene_astro_day" and \
            event.get("param") == "enable" and \
            not event.get("value")

    def handle(self, event: dict, context: Context) -> List[dict]:

        actions =  [
            {
                "type": "device_param_update",
                "device_id": "scene_dim",
                "param": "enable",
                "value": True
            }
        ]

        return actions
