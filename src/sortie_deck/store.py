from __future__ import annotations

import json
from pathlib import Path

from sortie_deck.models import Initiative, utc_now


class InitiativeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8") or "{}")

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def upsert(self, initiative: Initiative) -> Initiative:
        initiative.updated_at = utc_now()
        data = self._load()
        data[initiative.id] = json.loads(initiative.model_dump_json())
        self._save(data)
        return initiative

    def get(self, initiative_id: str) -> Initiative | None:
        data = self._load()
        raw = data.get(initiative_id)
        if not raw:
            return None
        return Initiative.model_validate(raw)

    def list(self) -> list[Initiative]:
        data = self._load()
        items = [Initiative.model_validate(v) for v in data.values()]
        return sorted(items, key=lambda i: i.created_at, reverse=True)

    def delete(self, initiative_id: str) -> None:
        data = self._load()
        data.pop(initiative_id, None)
        self._save(data)
