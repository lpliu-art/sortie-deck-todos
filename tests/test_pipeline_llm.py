from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from sortie_deck.llm import LlmClient
from sortie_deck.pipeline_llm import plan_pipeline_llm, plan_pipeline_smart


@pytest.mark.asyncio
async def test_plan_pipeline_smart_heuristic_default():
    proposal = await plan_pipeline_smart(title="typo", brief="一行代码改文案", use_llm=False)
    assert proposal["planner"] == "heuristic"
    assert proposal["status"] == "pending"
    assert proposal["stages"][0]["id"] == "intake"


@pytest.mark.asyncio
async def test_plan_pipeline_llm_uses_client(monkeypatch):
    client = LlmClient(api_key="test-key")
    stages = [
        {"id": "intake", "label": "Intake"},
        {"id": "eng_implement", "label": "Eng"},
        {"id": "qa_verify", "label": "QA"},
        {"id": "deploy_preview", "label": "Deploy"},
        {"id": "done", "label": "Done"},
    ]

    async def fake_json(**kwargs):
        return {
            "track_hint": "express",
            "rationale": "LLM says express",
            "stages": stages,
            "confidence": 0.7,
        }

    monkeypatch.setattr(client, "chat_json", fake_json)
    proposal = await plan_pipeline_llm(title="hot", brief="hotfix", client=client)
    assert proposal is not None
    assert proposal["planner"] == "llm"
    assert proposal["track_hint"] == "express"
    assert proposal["stages"][0]["id"] == "intake"


@pytest.mark.asyncio
async def test_plan_pipeline_smart_falls_back_when_llm_fails(monkeypatch):
    client = LlmClient(api_key="test-key", cli_fallback=False)
    monkeypatch.setattr(client, "chat_json", AsyncMock(side_effect=RuntimeError("boom")))
    proposal = await plan_pipeline_smart(
        title="x", brief="一行改文案", use_llm=True, client=client
    )
    assert proposal["planner"] == "heuristic"


@pytest.mark.asyncio
async def test_propose_loadout_llm(monkeypatch):
    from sortie_deck.pipeline_llm import propose_loadout_llm

    client = LlmClient(api_key="test-key", cli_fallback=False)

    async def fake_json(**kwargs):
        return {
            "needed_slots": ["product", "eng_web", "qa", "deploy"],
            "rationale": "web portal",
        }

    monkeypatch.setattr(client, "chat_json", fake_json)
    out = await propose_loadout_llm(
        brief="门户预发",
        stages=[{"id": "eng_web", "role": "eng_web"}],
        client=client,
    )
    assert out is not None
    assert out["needed_slots"] == ["product", "eng_web", "qa", "deploy"]
    assert out["planner"] == "llm"


def test_resolve_coding_executor_explicit():
    from sortie_deck.llm import resolve_coding_executor

    assert resolve_coding_executor("mock") == "mock"
    assert resolve_coding_executor("claude_code") == "claude_code"
    assert resolve_coding_executor("cursor_cli") == "cursor_cli"
