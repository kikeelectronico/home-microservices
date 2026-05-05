from typing import Iterable, List, Protocol
from shared.context import Context


class Handler(Protocol):
    def can_handle(self, event: dict) -> bool:
        ...

    def handle(self, event: dict, context: "Context") -> List[dict]:
        ...


class Engine:
    def __init__(self, handlers: Iterable[Handler]) -> None:
        self._handlers = list(handlers)

    def handle(self, event: dict, context: "Context") -> List[dict]:
        actions: List[dict] = []
        for handler in self._handlers:
            if handler.can_handle(event):
                actions.extend(handler.handle(event, context))
        return actions
