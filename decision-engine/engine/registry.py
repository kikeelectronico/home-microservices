from typing import List
from domains.air.quality.bathroom import BathroomAirQualityHandler
from domains.air.quality.livingroom import LivingroomAirQualityHandler
from domains.air.temperature.bathroom import BathroomAirTemperatureHandler
from domains.air.temperature.bedroom import BedroomAirTemperatureHandler
from domains.air.temperature.livingroom import LivingroomAirTemperatureHandler
from domains.light.bathroom_mirror import BathroomMirrorLightHandler
from domains.light.bathroom import BathroomLightHandler
from domains.light.bedroom_brightness import BedroomBrightnessLightHandler
from domains.light.bedroom import BedroomLightHandler
from domains.light.hallway_brightness import HallwayBrightnessLightHandler
from domains.light.hallway import HallwayLightHandler
from domains.light.kitchen import KitchenLightHandler
from domains.light.livingroom_fairy_brightness import LivingroomFairyBrightneesLightHandler
from domains.light.livingroom_pyramid import LivingroomPyramidLightHandler
from domains.light.livingroom_sofa import LivingroomSofaLightHandler
from domains.light.livingroom_table_brightness import LivingroomTableBrightnessLightHandler
from domains.light.livingroom_table_color import LivingroomTableColorLightHandler
from domains.light.livingroom import LivingroomLightHandler
from domains.light.office_brightness import OfficeBrightnessLightHandler
from domains.light.office import OfficeLightHandler
from domains.light.workbench import WorkbenchLightHandler
from domains.notification.message.battery import BatteryNotificationMessageHandler
from domains.notification.voice.battery import BatteryNotificationVoiceHandler
from domains.notification.voice.night_time import NightTimeVoiceNotificationHandler
from domains.presence.bathroom import BathroomPresenceHandler
from domains.presence.bedroom import BedroomPresenceHandler
from domains.presence.livingroom import LivingroomPresenceHandler
from domains.scenes.awake import AwakeSceneHandler
from domains.scenes.sensors import SensorsSceneHandler
from domains.scenes.dim import DimSceneHandler
from domains.scenes.shower import ShowerSceneHandler
from domains.switch.prepare_home import PrepareHomeSwitchHandler

from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        BathroomAirQualityHandler(),
        LivingroomAirQualityHandler(),
        BathroomAirTemperatureHandler(),
        BedroomAirTemperatureHandler(),
        LivingroomAirTemperatureHandler(),
        BathroomMirrorLightHandler(),
        BathroomLightHandler(),
        BedroomBrightnessLightHandler(),
        BedroomLightHandler(),
        HallwayBrightnessLightHandler(),
        HallwayLightHandler(),
        KitchenLightHandler(),
        LivingroomFairyBrightneesLightHandler(),
        LivingroomPyramidLightHandler(),
        LivingroomSofaLightHandler(),
        LivingroomTableBrightnessLightHandler(),
        LivingroomTableColorLightHandler(),
        LivingroomLightHandler(),
        OfficeBrightnessLightHandler(),
        OfficeLightHandler(),
        WorkbenchLightHandler(),
        BatteryNotificationMessageHandler(),
        BatteryNotificationVoiceHandler(),
        NightTimeVoiceNotificationHandler(),
        BathroomPresenceHandler(),
        BedroomPresenceHandler(),
        LivingroomPresenceHandler(),
        AwakeSceneHandler(),
        DimSceneHandler(),
        ShowerSceneHandler(),
        SensorsSceneHandler(),
        PrepareHomeSwitchHandler(),
    ]
