from typing import Any, Dict


class Context:
    def __init__(self, state: Dict[str, Any]) -> None:
        self._state = dict(state)

    def get(self, key: str) -> Any:
        return self._state.get(key)
