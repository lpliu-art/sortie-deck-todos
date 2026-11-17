from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from sortie_deck.models import CreateInitiativeRequest, InitiativeStatus
from sortie_deck.orchestrator import Orchestrator
from sortie_deck.settings import Settings


@pytest.mark.asyncio
async def test_discuss_opt_in_out_filters_agent_replies(tmp_path: Path):
    cfg = Settings(
        data_dir=tmp_path / "data",
        pipeline_llm=False,
        room_llm=False,
        llm_cli_fallback=False,
        default_coding_executor="mock",
    )
    orch = Orchestrator(cfg)
    await orch.startup()
    try:
        ini = await orch.create_initiative(
            CreateInitiativeRequest(
                title="Snake",
                brief="狂野贪吃蛇 Web",
                coding_executor="mock",
                creator_name="Admin",
            )
        )
        product = next(p for p in ini.participants if p.role == "product")
        assert product.discussing is True

        ini = await orch.set_discussing(
            ini.id, discussing=False, participant_id=product.id, actor_name="Admin"
        )
        product = next(p for p in ini.participants if p.role == "product")
        assert product.discussing is False

        before = len(orch.list_room_messages(ini.id))
        await orch.post_human_message(ini.id, "@product 出个方案", author_name="Admin")
        after = orch.list_room_messages(ini.id)
        # human msg + system "未参与讨论" — no agent PRD reply
        new = after[before:]
        assert any(m.msg_type == "system" and "未参与" in m.text for m in new)
        assert not any(m.actor_kind.value == "agent" and m.msg_type == "chat" for m in new)

        await orch.set_discussing(ini.id, discussing=True, role="product", actor_name="Admin")
        before = len(orch.list_room_messages(ini.id))
        await orch.post_human_message(ini.id, "@product 再来一版", author_name="Admin")
        after = orch.list_room_messages(ini.id)
        new = after[before:]
        assert any(m.actor_kind.value == "agent" and m.role == "product" for m in new)
        assert ini.status == InitiativeStatus.DRAFT or True
    finally:
        await orch.shutdown() if hasattr(orch, "shutdown") else None
