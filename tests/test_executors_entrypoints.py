from __future__ import annotations

from sortie_deck.plugins.entrypoints import load_entry_point_executors, probe_executor
from sortie_deck.plugins.factory import build_default_registry
from sortie_deck.registry import ExecutorRegistry


def test_registry_includes_builtins():
    reg = build_default_registry()
    names = reg.names()
    assert "mock_eng" in names
    assert "claude_code" in names


def test_probe_executor():
    class E:
        name = "x"

        def probe(self):
            return {"status": "ok", "detail": "fine"}

    assert probe_executor(E())["status"] == "ok"


def test_load_entry_points_tolerates_empty():
    reg = ExecutorRegistry()
    loaded = load_entry_point_executors(reg)
    assert isinstance(loaded, list)
