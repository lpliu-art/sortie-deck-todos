from __future__ import annotations

import json
from pathlib import Path

from sortie_deck.models import RoomMessage


class RoomStore:
    """Per-initiative discussion room (Matrix-room inspired, local files)."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, initiative_id: str) -> Path:
        return self.root / f"{initiative_id}.jsonl"

    def append(self, message: RoomMessage) -> RoomMessage:
        path = self._path(message.initiative_id)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(message.model_dump_json() + "\n")
        return message

    def list(self, initiative_id: str, limit: int = 500) -> list[RoomMessage]:
        path = self._path(initiative_id)
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        msgs: list[RoomMessage] = []
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            msgs.append(RoomMessage.model_validate(json.loads(line)))
        return msgs

    def clear(self, initiative_id: str) -> None:
        path = self._path(initiative_id)
        if path.exists():
            path.unlink()
