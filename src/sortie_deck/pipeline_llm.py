from __future__ import annotations

import json
from typing import Any

from sortie_deck.llm import LlmClient
from sortie_deck.pipeline import (
    PLANNER_AGENT,
    PLANNER_TITLE,
    TRACK_FILES,
    catalog_by_id,
    normalize_specs,
    plan_pipeline,
    resolve_track,
)

_SYSTEM = """You are Sortie Deck's pipeline_planner agent.
Propose a software delivery pipeline as JSON with keys:
  track_hint: one of express|standard|default
  rationale: short Chinese or English explanation
  stages: array of {id, label?, role?, hitl_after?, parallel_group?, branch?, depends_on?}
Only use stage ids from the provided catalog. Always include intake first and done last.
When multiple eng_* specialists (eng_web, eng_backend, eng_ios, …) should run together,
emit independent branch chains — not a shared selftest:
  eng_web → eng_web_selftest (branch=web, parallel_group=eng_delivery)
  eng_backend → eng_backend_selftest (branch=backend, parallel_group=eng_delivery)
then eng_integrate. Set depends_on for each stage (fan-out from previous trunk, fan-in into integrate).
Do NOT use a single shared eng_selftest when multiple platforms are present.
Human confirmation is mandatory after your proposal — never assume start.
Return ONLY JSON.
"""

_LOADOUT_SYSTEM = """You are Sortie Deck's squad loadout planner.
Given a mission brief and proposed pipeline stages, return JSON:
  needed_slots: array of role ids from
    [product, design, eng, eng_ios, eng_android, eng_web, eng_backend, eng_agent, qa, deploy]
  rationale: short explanation in the same language as the brief
Only include slots that the stages / brief actually need. Always include product, qa, deploy
when those stages exist. Prefer specialized eng_* over generic eng when platforms are clear.
Return ONLY JSON.
"""

_VALID_SLOTS = {
    "product",
    "design",
    "eng",
    "eng_ios",
    "eng_android",
    "eng_web",
    "eng_backend",
    "eng_agent",
    "qa",
    "deploy",
}


async def plan_pipeline_llm(
    *,
    title: str = "",
    brief: str = "",
    hint_track: str | None = None,
    complexity: str = "auto",
    client: LlmClient | None = None,
) -> dict[str, Any] | None:
    """Optional LLM planner. Returns None on failure so caller can fall back."""
    llm = client or LlmClient()
    if not llm.enabled:
        return None
    catalog = catalog_by_id()
    catalog_summary = [
        {"id": s["id"], "label": s.get("label"), "role": s.get("role")} for s in catalog.values()
    ]
    hint = hint_track if hint_track in TRACK_FILES else None
    user = json.dumps(
        {
            "title": title,
            "brief": brief,
            "complexity": complexity,
            "hint_track": hint,
            "catalog": catalog_summary,
        },
        ensure_ascii=False,
    )
    try:
        data = await llm.chat_json(system=_SYSTEM, user=user)
    except Exception:
        return None

    track = data.get("track_hint")
    if track not in TRACK_FILES:
        track, _ = resolve_track(complexity=complexity, brief=brief, title=title)
    try:
        stages = normalize_specs(data.get("stages") or [])
    except Exception:
        return None
    if not stages:
        return None

    return {
        "agent": PLANNER_AGENT,
        "agent_title": PLANNER_TITLE,
        "track_hint": track,
        "rationale": data.get("rationale")
        or f"LLM planner proposed `{track}` stages pending human confirm.",
        "notes": [f"planner=llm:{llm.backend}"],
        "stages": stages,
        "status": "pending",
        "planner": "llm",
        "planner_backend": llm.backend,
        "confidence": float(data.get("confidence") or 0.6),
    }


async def propose_loadout_llm(
    *,
    brief: str = "",
    stages: list[dict[str, Any]] | None = None,
    client: LlmClient | None = None,
) -> dict[str, Any] | None:
    """LLM squad loadout. Returns None on failure."""
    llm = client or LlmClient()
    if not llm.enabled:
        return None
    user = json.dumps(
        {
            "brief": brief,
            "stages": [
                {"id": s.get("id"), "role": s.get("role"), "label": s.get("label")}
                for s in (stages or [])
                if isinstance(s, dict)
            ],
        },
        ensure_ascii=False,
    )
    try:
        data = await llm.chat_json(system=_LOADOUT_SYSTEM, user=user)
    except Exception:
        return None
    slots = [str(s) for s in (data.get("needed_slots") or []) if str(s) in _VALID_SLOTS]
    if not slots:
        return None
    seen: set[str] = set()
    ordered: list[str] = []
    for s in slots:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return {
        "needed_slots": ordered,
        "rationale": str(data.get("rationale") or ""),
        "planner": "llm",
        "planner_backend": llm.backend,
    }


async def plan_pipeline_smart(
    *,
    title: str = "",
    brief: str = "",
    hint_track: str | None = None,
    complexity: str = "auto",
    use_llm: bool = False,
    client: LlmClient | None = None,
) -> dict[str, Any]:
    if use_llm:
        llm_proposal = await plan_pipeline_llm(
            title=title,
            brief=brief,
            hint_track=hint_track,
            complexity=complexity,
            client=client,
        )
        if llm_proposal:
            return llm_proposal
    proposal = plan_pipeline(
        title=title,
        brief=brief,
        hint_track=hint_track,
        complexity=complexity,
    )
    proposal["planner"] = "heuristic"
    proposal.setdefault("confidence", 0.85)
    return proposal
