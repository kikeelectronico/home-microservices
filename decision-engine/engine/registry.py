from typing import List
from domains.lighting.button_lighting import ButtonLightingHandler
from domains.lighting.hallway import HallwayLightHandler
from domains.scenes.sensors import SensorsSceneHandler
from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        ButtonLightingHandler(),
        HallwayLightHandler(),
        SensorsSceneHandler(),
    ]
