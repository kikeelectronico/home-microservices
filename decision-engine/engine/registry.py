from typing import List
from domains.air.quality.livingroom import LivingroomAirQualityHandler
from domains.light.bathroom import BathroomLightHandler
from domains.light.bedroom import BedroomLightHandler
from domains.light.hallway import HallwayLightHandler
from domains.light.livingroom_table import LivingroomTableLightHandler
from domains.light.livingroom_fairy import LivingroomFairyLightHandler
from domains.light.livingroom import LivingroomLightHandler
from domains.presence.bathroom import BathroomPresenceHandler
from domains.presence.bedroom import BedroomPresenceHandler
from domains.presence.livingroom import LivingroomPresenceHandler
from domains.scenes.sensors import SensorsSceneHandler
from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        LivingroomAirQualityHandler(),
        BathroomLightHandler(),
        BedroomLightHandler(),
        HallwayLightHandler(),
        LivingroomTableLightHandler(),
        LivingroomFairyLightHandler(),
        LivingroomLightHandler(),
        BathroomPresenceHandler(),
        BedroomPresenceHandler(),
        LivingroomPresenceHandler(),
        SensorsSceneHandler(),
    ]
