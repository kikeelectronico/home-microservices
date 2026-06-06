from typing import List
from domains.lighting.button_lighting import ButtonLightingHandler
from domains.lighting.bathroom import BathroomLightHandler
from domains.lighting.bedroom import BedroomLightHandler
from domains.lighting.hallway import HallwayLightHandler
from domains.presence.bathroom import BathroomPresenceHandler
from domains.presence.bedroom import BedroomPresenceHandler
from domains.presence.livingroom import LivingroomPresenceHandler
from domains.scenes.sensors import SensorsSceneHandler
from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        ButtonLightingHandler(),
        BathroomLightHandler(),
        BedroomLightHandler(),
        HallwayLightHandler(),
        BathroomPresenceHandler(),
        BedroomPresenceHandler(),
        LivingroomPresenceHandler(),
        SensorsSceneHandler(),
    ]
