from __future__ import annotations

from sortie_deck.knowledge import (
    CreateKnowledgeRequest,
    KnowledgeStore,
    UpdateKnowledgeRequest,
)


def test_knowledge_crud_and_seed(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.json")
    seeded = store.list()
    assert len(seeded) >= 3
    assert any("作战手册" in d.title or "Playbook" in d.title or "Fireteam" in d.title for d in seeded)

    created = store.create(
        CreateKnowledgeRequest(
            title="Customer X stack",
            summary="React + FastAPI",
            body="# Notes\nPrefer SSE.",
            tags=["customer-x", "stack"],
            category="reference",
        ),
        author_id="usr_1",
        author_name="Ada",
    )
    assert created.id.startswith("kb_")
    assert store.get(created.id).author_name == "Ada"

    updated = store.update(
        created.id,
        UpdateKnowledgeRequest(summary="React + FastAPI + Redis"),
    )
    assert "Redis" in updated.summary
    assert store.list(q="redis")
    store.delete(created.id)
    assert all(d.id != created.id for d in store.list())


def test_knowledge_search_title_tag_body(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.json")
    doc = store.create(
        CreateKnowledgeRequest(
            title="UniqueTitleMarker",
            summary="plain summary",
            body="Body holds UniqueBodyToken.",
            tags=["UniqueTagMarker"],
            category="reference",
        ),
        author_id="u1",
        author_name="Ada",
    )
    assert any(d.id == doc.id for d in store.list(q="uniquetitlemarker"))
    assert any(d.id == doc.id for d in store.list(q="uniquebodytoken"))
    assert any(d.id == doc.id for d in store.list(q="uniquetagmarker"))
    store.delete(doc.id)


def test_knowledge_seed_cross_links(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.json")
    bodies = {d.title: d.body for d in store.list()}
    assert "mission-clearance" in bodies["Fireteam 作战手册"]
    assert "fireteam-playbook" in bodies["Mission Clearance 门禁规则"]
    assert "mission-clearance" in bodies["Codex 写入约定"]
