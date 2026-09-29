from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

from sortie_deck.registry import ExecutorRegistry

# Preferred group + legacy Rally group for installed community plugins.
_EXECUTOR_GROUPS = ("sortie_deck.executors", "rally.executors")


def load_entry_point_executors(registry: ExecutorRegistry) -> list[str]:
    """Load community executors from Sortie Deck (and legacy Rally) entry-point groups."""
    loaded: list[str] = []
    seen: set[str] = set()
    for group in _EXECUTOR_GROUPS:
        try:
            try:
                eps = entry_points(group=group)
            except TypeError:
                # Python <3.12 compatibility path
                eps = entry_points().select(group=group)  # type: ignore[attr-defined]
        except Exception:
            continue
        for ep in eps:
            try:
                factory = ep.load()
                executor = factory() if callable(factory) else factory
                if hasattr(executor, "name") and hasattr(executor, "run"):
                    name = str(executor.name)
                    if name in seen:
                        continue
                    registry.register(executor)
                    seen.add(name)
                    loaded.append(name)
            except Exception:
                continue
    return loaded


def probe_executor(executor: Any) -> dict[str, Any]:
    name = getattr(executor, "name", type(executor).__name__)
    return {
        "name": name,
        "ok": hasattr(executor, "run"),
        "module": type(executor).__module__,
    }
