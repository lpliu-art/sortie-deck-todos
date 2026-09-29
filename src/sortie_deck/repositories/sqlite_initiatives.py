from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from sortie_deck.models import Initiative, utc_now


class SqliteInitiativeStore:
    """SQLite-backed initiative repository (JSON document per row)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS initiatives (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def upsert(self, initiative: Initiative) -> Initiative:
        initiative.updated_at = utc_now()
        payload = initiative.model_dump_json()
        self._conn.execute(
            """
            INSERT INTO initiatives (id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              payload=excluded.payload,
              updated_at=excluded.updated_at
            """,
            (initiative.id, payload, initiative.updated_at.isoformat()),
        )
        self._conn.commit()
        return initiative

    def get(self, initiative_id: str) -> Initiative | None:
        row = self._conn.execute(
            "SELECT payload FROM initiatives WHERE id = ?", (initiative_id,)
        ).fetchone()
        if not row:
            return None
        return Initiative.model_validate(json.loads(row[0]))

    def list(self) -> list[Initiative]:
        rows = self._conn.execute("SELECT payload FROM initiatives").fetchall()
        items = [Initiative.model_validate(json.loads(r[0])) for r in rows]
        return sorted(items, key=lambda i: i.created_at, reverse=True)

    def delete(self, initiative_id: str) -> None:
        self._conn.execute("DELETE FROM initiatives WHERE id = ?", (initiative_id,))
        self._conn.commit()
