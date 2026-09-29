from __future__ import annotations

from pathlib import Path

from sortie_deck.repositories.protocol import InitiativeRepository
from sortie_deck.repositories.sqlite_initiatives import SqliteInitiativeStore
from sortie_deck.store import InitiativeStore


def build_initiative_store(
    *,
    storage: str,
    json_path: Path,
    sqlite_path: Path,
) -> InitiativeRepository:
    backend = (storage or "json").strip().lower()
    if backend in {"sqlite", "sql"}:
        return SqliteInitiativeStore(sqlite_path)
    return InitiativeStore(json_path)
