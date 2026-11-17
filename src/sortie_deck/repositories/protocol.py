from __future__ import annotations

from typing import Protocol, runtime_checkable

from sortie_deck.models import Initiative


@runtime_checkable
class InitiativeRepository(Protocol):
    def upsert(self, initiative: Initiative) -> Initiative: ...

    def get(self, initiative_id: str) -> Initiative | None: ...

    def list(self) -> list[Initiative]: ...

    def delete(self, initiative_id: str) -> None: ...
