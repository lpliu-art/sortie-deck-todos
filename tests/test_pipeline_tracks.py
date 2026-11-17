from __future__ import annotations

import asyncio

import pytest

from sortie_deck.models import (
    ConfirmPipelineRequest,
    CreateInitiativeRequest,
    PipelineNotConfirmedError,
    PipelineStageSpec,
    UpdatePipelineRequest,
)
from sortie_deck.orchestrator import Orchestrator
from sortie_deck.pipeline import plan_pipeline, suggest_track
from sortie_deck.settings import Settings


def test_suggest_track_trivial_and_standard():
    track, reason = suggest_track("改一行文案 hotfix")
    assert track == "express"
    assert "express" in reason
    track2, _ = suggest_track("新做支付权限体系重构平台级需求")
    assert track2 == "standard"


def test_planner_adds_design_and_specialist_eng():
    proposal = plan_pipeline(
        title="多端门户",
        brief="需要设计和 PRD；实现 iOS Android Web 后端与 Agent 开发",
        hint_track="standard",
    )
    ids = [s["id"] for s in proposal["stages"]]
    assert "design_ui" in ids
    assert "eng_implement" not in ids
    for sid in ("eng_ios", "eng_android", "eng_web", "eng_backend", "eng_agent"):
        assert sid in ids
    assert ids.index("design_ui") < ids.index("eng_ios")


def test_planner_keeps_generic_eng_without_platform_signals():
    proposal = plan_pipeline(
        title="文案微调",
        brief="改一下首页标题文案",
        hint_track="express",
    )
    ids = [s["id"] for s in proposal["stages"]]
    assert "eng_implement" in ids
    assert "design_ui" not in ids
    assert "eng_ios" not in ids


def test_planner_agent_proposes_pending_then_confirm(tmp_path):
    cfg = Settings(data_dir=tmp_path / "data", deploy_executor="mock")
    orch = Orchestrator(cfg)

    async def _run():
        await orch.startup()
        try:
            proposal = plan_pipeline(title="typo", brief="一行代码改文案")
            assert proposal["agent"] == "pipeline_planner"
            assert proposal["status"] == "pending"
            assert "eng_implement" in [s["id"] for s in proposal["stages"]]

            ini = await orch.create_initiative(
                CreateInitiativeRequest(
                    title="typo",
                    brief="一行代码改文案",
                    creator_name="Ada",
                )
            )
            assert ini.meta.get("pipeline_confirmed") is False
            assert ini.meta.get("pipeline_proposal", {}).get("status") == "pending"

            # Cannot start before confirm
            with pytest.raises(PipelineNotConfirmedError) as err:
                await orch.start_pipeline(ini.id)
            assert err.value.code == "pipeline_not_confirmed"

            # Manual edit: drop deploy hitl by removing nothing, just reorder-ish via patch
            specs = [
                PipelineStageSpec(**{k: s[k] for k in ("id", "label", "role", "hitl_after") if k in s})
                for s in ini.meta["pipeline_specs"]
            ]
            # remove qa_verify temporarily then add back via catalog-less edit — keep eng+deploy
            edited = [s for s in specs if s.id != "qa_verify"]
            ini = await orch.update_pipeline(
                ini.id,
                UpdatePipelineRequest(stages=edited, confirm=False),
                author_name="Ada",
            )
            assert "qa_verify" not in ini.meta["pipeline_stages"]
            assert ini.meta["pipeline_confirmed"] is False

            ini = await orch.confirm_pipeline(
                ini.id, ConfirmPipelineRequest(), author_name="Ada"
            )
            assert ini.meta["pipeline_confirmed"] is True
            assert f"custom:{ini.id}" in orch.graphs

            # standard proposal has full nodes
            std = await orch.create_initiative(
                CreateInitiativeRequest(
                    title="Feature",
                    brief="正常需求：账号中心改版",
                    pipeline_track="standard",
                    creator_name="Ada",
                )
            )
            stages = std.meta["pipeline_stages"]
            assert "product_prd" in stages and "qa_cases" in stages
            assert "design_ui" in stages
        finally:
            await orch.shutdown()

    asyncio.run(_run())
