from __future__ import annotations

from typing import Protocol

from sortie_deck.models import StageContext, StageResult


class StageExecutor(Protocol):
    name: str

    async def run(self, ctx: StageContext) -> StageResult: ...


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[str, StageExecutor] = {}

    def register(self, executor: StageExecutor) -> None:
        self._executors[executor.name] = executor

    def get(self, name: str) -> StageExecutor:
        if name not in self._executors:
            raise KeyError(f"Unknown executor: {name}")
        return self._executors[name]

    def names(self) -> list[str]:
        return sorted(self._executors)


_REGISTRY: ExecutorRegistry | None = None


def get_registry() -> ExecutorRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        from sortie_deck.plugins.factory import build_default_registry

        _REGISTRY = build_default_registry()
    return _REGISTRY


def reset_registry() -> None:
    global _REGISTRY
    _REGISTRY = None
