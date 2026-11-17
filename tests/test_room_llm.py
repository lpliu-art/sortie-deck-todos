from __future__ import annotations

import pytest

from sortie_deck.models import Initiative, RoleAgent, RoleId
from sortie_deck.room_llm import craft_discussion_reply_llm, craft_discussion_reply_template
from sortie_deck.rooms import RoomStore


def test_template_discussion_reply():
    ini = Initiative(title="T", brief="B" * 40)
    role = RoleAgent(
        id="r1", role=RoleId.PRODUCT, title="产品", persona="pm", executor="mock"
    )
    text = craft_discussion_reply_template(ini, role, "hello", "Alice")
    assert "Alice" in text
    assert "T" in text


@pytest.mark.asyncio
async def test_room_llm_returns_none_without_key(tmp_path):
    from sortie_deck.llm import LlmClient

    ini = Initiative(title="T", brief="brief")
    role = RoleAgent(
        id="r2", role=RoleId.ENG, title="工程", persona="eng", executor="mock"
    )
    rooms = RoomStore(tmp_path / "rooms")
    reply = await craft_discussion_reply_llm(
        ini=ini,
        role=role,
        text="@eng hi",
        author_name="Bob",
        rooms=rooms,
        client=LlmClient(api_key="", cli_fallback=False),
    )
    assert reply is None
