from __future__ import annotations

from sortie_deck.knowledge import KnowledgeDoc, KnowledgeStore
from sortie_deck.knowledge_pack import (
    load_pack_for_cursor,
    render_knowledge_pack,
    score_doc,
    search_for_mission,
)


def test_score_and_search(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.json")
    # force enterprise-ish docs via create
    from sortie_deck.knowledge import CreateKnowledgeRequest

    store.create(
        CreateKnowledgeRequest(
            title="Payment API",
            summary="charge endpoint",
            body="POST /v1/charges",
            tags=["api", "openapi"],
            category="reference",
        ),
        author_id="u1",
        author_name="t",
    )
    store.create(
        CreateKnowledgeRequest(
            title="Unrelated cookbook",
            summary="pasta",
            body="boil water",
            tags=["food"],
            category="lore",
        ),
        author_id="u1",
        author_name="t",
    )
    hits = search_for_mission(store, "implement payment charges API openapi", limit=3)
    assert hits
    assert "Payment" in hits[0][0].title
    assert score_doc(hits[0][0], "payment api") > score_doc(
        KnowledgeDoc(title="x", body="y"), "payment api"
    )


def test_load_pack_for_cursor(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.json")
    from sortie_deck.knowledge import CreateKnowledgeRequest

    store.create(
        CreateKnowledgeRequest(
            title="Portal health",
            summary="health check",
            body="GET /api/health",
            tags=["api", "portal", "health"],
            category="reference",
        ),
        author_id="u1",
        author_name="t",
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    meta = load_pack_for_cursor(store, ws, "office portal preview health endpoint")
    assert (ws / meta["rule"]).exists()
    assert (ws / meta["pack"]).exists()
    text = (ws / meta["rule"]).read_text(encoding="utf-8")
    assert "alwaysApply" in text
    assert "Portal health" in text or "health" in text.lower()
    pack = render_knowledge_pack(search_for_mission(store, "portal health"), query="portal")
    assert "Sortie Deck knowledge pack" in pack
