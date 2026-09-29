from __future__ import annotations

from sortie_deck.models import Initiative, InitiativeStatus
from sortie_deck.repositories import SqliteInitiativeStore, build_initiative_store


def test_sqlite_initiative_roundtrip(tmp_path):
    store = SqliteInitiativeStore(tmp_path / "initiatives.sqlite")
    ini = Initiative(title="SQL mission", brief="persist me", status=InitiativeStatus.DRAFT)
    store.upsert(ini)
    got = store.get(ini.id)
    assert got is not None
    assert got.title == "SQL mission"
    assert any(i.id == ini.id for i in store.list())
    store.delete(ini.id)
    assert store.get(ini.id) is None


def test_factory_selects_backend(tmp_path):
    json_store = build_initiative_store(
        storage="json",
        json_path=tmp_path / "initiatives.json",
        sqlite_path=tmp_path / "initiatives.sqlite",
    )
    sqlite_store = build_initiative_store(
        storage="sqlite",
        json_path=tmp_path / "initiatives.json",
        sqlite_path=tmp_path / "initiatives.sqlite",
    )
    assert type(json_store).__name__ == "InitiativeStore"
    assert type(sqlite_store).__name__ == "SqliteInitiativeStore"
