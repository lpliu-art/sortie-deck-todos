from __future__ import annotations

import pytest

from sortie_deck.agents import (
    AgentCatalog,
    CreateAgentRequest,
    UpdateAgentRequest,
)
from sortie_deck.memory import (
    CONTEXT_BLOCK_MAX_CHARS,
    CreateMemoryRequest,
    MemoryStore,
    UpdateMemoryRequest,
)


def test_memory_scopes_and_context(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    assert store.list(scope="workspace")
    mine = store.create(
        CreateMemoryRequest(scope="user", kind="preference", content="Prefer TypeScript."),
        author_id="usr_a",
        author_name="Ada",
    )
    assert mine.scope_id == "usr_a"
    store.create(
        CreateMemoryRequest(
            scope="mission",
            scope_id="ini_1",
            kind="episode",
            content="Customer wants SSO first.",
            tags=["customer"],
        ),
        author_id="usr_a",
        author_name="Ada",
    )
    brief = store.context_block(user_id="usr_a", mission_id="ini_1")
    assert "TypeScript" in brief
    assert "SSO" in brief
    store.update(mine.id, UpdateMemoryRequest(content="Prefer TypeScript strict."))
    store.delete(mine.id)


def test_agent_catalog_publish_and_slot_map(tmp_path):
    catalog = AgentCatalog(tmp_path / "agents.json")
    assert len(catalog.list()) >= 3
    created = catalog.create(
        CreateAgentRequest(
            title="Payments QA",
            slot="qa",
            summary="Knows PCI + refund paths",
            persona="You are a payments QA specialist.",
            tags=["payments", "qa"],
        ),
        author_id="usr_b",
        author_name="Bob",
    )
    assert created.slug
    mapped = catalog.resolve_slot_map({"qa": created.id})
    assert "qa" in {r.value for r in mapped}
    catalog.update(
        created.id,
        UpdateAgentRequest(summary="PCI + refund + chargeback"),
        editor_id="usr_b",
        is_admin=False,
    )
    catalog.delete(created.id, editor_id="usr_b", is_admin=False)


def test_non_author_cannot_update_or_delete_agent(tmp_path):
    catalog = AgentCatalog(tmp_path / "agents.json")
    agent = catalog.create(
        CreateAgentRequest(
            title="Owner only",
            slot="eng",
            summary="private edits",
            persona="Eng persona",
        ),
        author_id="owner",
        author_name="Owner",
    )
    with pytest.raises(PermissionError):
        catalog.update(
            agent.id,
            UpdateAgentRequest(summary="hijacked"),
            editor_id="intruder",
            is_admin=False,
        )
    with pytest.raises(PermissionError):
        catalog.delete(agent.id, editor_id="intruder", is_admin=False)


def test_memory_context_block_truncates(tmp_path):
    store = MemoryStore(tmp_path / "memory.json")
    for i in range(40):
        store.create(
            CreateMemoryRequest(scope="workspace", kind="fact", content=f"Line {i}: " + ("x" * 400)),
            author_id="u1",
            author_name="Ada",
        )
    block = store.context_block(limit=40)
    assert block.startswith("Memory brief:")
    assert len(block) <= CONTEXT_BLOCK_MAX_CHARS
    assert block.endswith("...")
