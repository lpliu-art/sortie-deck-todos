from __future__ import annotations

import pytest

from sortie_deck.models import CreateInitiativeRequest
from sortie_deck.orchestrator import Orchestrator
from sortie_deck.settings import Settings


@pytest.mark.asyncio
async def test_room_discussion_before_pipeline(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", deploy_executor="mock")
    orch = Orchestrator(cfg)
    await orch.startup()
    try:
        ini = await orch.create_initiative(
            CreateInitiativeRequest(
                title="Chat first",
                brief="Need a notification center",
                creator_name="Alice",
                auto_start=False,
            )
        )
        assert ini.status.value == "draft"
        msgs = orch.list_room_messages(ini.id)
        assert any(m.msg_type == "system" for m in msgs)

        await orch.join_room(ini.id, "Bob", title="PM")
        msg, _ = await orch.post_human_message(
            ini.id, "@product 验收标准怎么定？", author_name="Bob"
        )
        assert msg.actor_kind.value == "human"
        room = orch.list_room_messages(ini.id)
        assert any(m.actor_kind.value == "agent" and m.role == "product" for m in room)

        _, confirmed = await orch.post_human_message(ini.id, "/confirm", author_name="Alice")
        assert confirmed is not None
        assert confirmed.meta.get("pipeline_confirmed") is True

        _, started = await orch.post_human_message(ini.id, "/start", author_name="Alice")
        assert started is not None
        assert started.status.value in {"running", "waiting_hitl"}
    finally:
        await orch.shutdown()
