from typing import List
from domains.air.quality.livingroom import LivingroomAirQualityHandler
from domains.notification.voice.night_time import NightTimeVoiceNotificationHandler
from domains.light.bathroom_mirror import BathroomMirrorLightHandler
from domains.light.bathroom import BathroomLightHandler
from domains.light.bedroom_brightness import BedroomBrightnessLightHandler
from domains.light.bedroom import BedroomLightHandler
from domains.light.hallway_brightness import HallwayBrightnessLightHandler
from domains.light.hallway import HallwayLightHandler
from domains.light.livingroom_fairy import LivingroomFairyLightHandler
from domains.light.livingroom_pyramid import LivingroomPyramidLightHandler
from domains.light.livingroom_table import LivingroomTableLightHandler
from domains.light.livingroom import LivingroomLightHandler
from domains.light.office import OfficeLightHandler
from domains.presence.bathroom import BathroomPresenceHandler
from domains.presence.bedroom import BedroomPresenceHandler
from domains.presence.livingroom import LivingroomPresenceHandler
from domains.scenes.sensors import SensorsSceneHandler
from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        LivingroomAirQualityHandler(),
        NightTimeVoiceNotificationHandler(),
        BathroomMirrorLightHandler(),
        BathroomLightHandler(),
        BedroomBrightnessLightHandler(),
        BedroomLightHandler(),
        HallwayBrightnessLightHandler(),
        HallwayLightHandler(),
        LivingroomFairyLightHandler(),
        LivingroomPyramidLightHandler(),
        LivingroomTableLightHandler(),
        LivingroomLightHandler(),
        OfficeLightHandler(),
        BathroomPresenceHandler(),
        BedroomPresenceHandler(),
        LivingroomPresenceHandler(),
        SensorsSceneHandler(),
    ]
