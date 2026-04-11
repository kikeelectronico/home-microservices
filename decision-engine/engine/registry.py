from typing import List
from domains.lighting.button_lighting import ButtonLightingHandler
from engine.engine import Handler


def build_handlers() -> List[Handler]:
    return [
        ButtonLightingHandler(),
    ]
