from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, TypedDict

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from sortie_deck.artifacts import ArtifactStore
from sortie_deck.contracts import validate_stage_artifacts
from sortie_deck.models import (
    CODING_ROLE_VALUES,
    ENG_BUILD_STAGES,
    HitlAction,
    HitlDecision,
    RoleId,
    StageContext,
    StageResult,
)
from sortie_deck.plugins.queue import ENG_QUEUE
from sortie_deck.parallel import collapse_to_waves, wave_node_name
from sortie_deck.registry import ExecutorRegistry
from sortie_deck.templates import load_persona, load_pipeline_template


def _coding_perm_from_instruction(instruction: str | None) -> dict[str, str]:
    """Parse Sortie Deck retry tag from human_instruction into StageContext.permissions."""
    text = instruction or ""
    markers = (
        "[sortie:coding_permission_mode=",
        "[rally:coding_permission_mode=",  # legacy
    )
    mode = ""
    for marker in markers:
        if marker not in text:
            continue
        try:
            rest = text.split(marker, 1)[1]
            mode = rest.split("]", 1)[0].strip()
        except Exception:
            mode = ""
        if mode:
            break
    if not mode:
        return {}
    return {"coding_permission_mode": mode}


class PipelineState(TypedDict, total=False):
    initiative_id: str
    thread_id: str
    brief: str
    title: str
    stage: str
    human_instruction: str | None
    coding_executor: str
    deploy_executor: str
    artifact_root: str
    workspace_dir: str | None
    upstream: dict[str, str]
    last_result: dict[str, Any]
    qa_attempt: int
    hitl_decision: dict[str, Any] | None
    stopped: bool
    events: list[dict[str, Any]]
    status: str
    pipeline_track: str
    role_personas: dict[str, str]
    role_toolkits: dict[str, list[str]]
    stage_toolkits: dict[str, list[str]]
    toolkit_briefs: dict[str, str]


def _role_id(role: str) -> RoleId:
    try:
        return RoleId(role)
    except ValueError:
        return RoleId.PRODUCT


def _executor_name(stage: str, role: str, state: PipelineState, stage_cfg: dict[str, Any]) -> str:
    explicit = stage_cfg.get("executor")
    if explicit:
        return str(explicit)
    if stage == "intake":
        return "mock_intake"
    if stage == "product_prd":
        return "mock_product"
    if stage == "design_ui":
        return "mock_design"
    if stage in ENG_BUILD_STAGES or stage in {"eng_selftest", "eng_integrate", "qa_handoff"} or stage.endswith(
        "_selftest"
    ):
        if stage in ENG_BUILD_STAGES:
            coding = state.get("coding_executor", "mock")
            return {
                "mock": "mock_eng",
                "claude_code": "claude_code",
                "cursor_cli": "cursor_cli",
            }.get(coding, "mock_eng")
        if stage == "eng_selftest" or stage.endswith("_selftest"):
            return "mock_selftest"
        if stage == "eng_integrate":
            return "mock_integrate"
        return "mock_handoff"
    if stage == "qa_cases":
        return "mock_qa_cases"
    if stage == "qa_verify":
        return "mock_qa"
    if stage == "deploy_preview":
        deploy = state.get("deploy_executor", "mock")
        return "deploy_shell" if deploy == "deploy_shell" else "mock_deploy"
    # fallback by role
    if role in CODING_ROLE_VALUES:
        return "mock_eng"
    return {
        "product": "mock_product",
        "design": "mock_design",
        "eng": "mock_eng",
        "qa": "mock_qa",
        "deploy": "mock_deploy",
    }.get(role, "mock_intake")


def _linear_next(stages: list[dict[str, Any]], index: int) -> str:
    """Next graph node after stages[index], collapsing parallel members into their wave."""
    if index + 1 >= len(stages):
        return "done"
    nxt = stages[index + 1]
    group = (nxt.get("parallel_group") or "").strip()
    if group and nxt.get("name") not in {"intake", "done"}:
        return wave_node_name(group)
    return nxt["name"]


def _resolve_goto(stages: list[dict[str, Any]], target: str | None) -> str:
    """Map a stage id to the graph node to enter (wave node if parallel member)."""
    if not target:
        return "done"
    if target.startswith("__wave__"):
        return target
    stage = next((s for s in stages if s.get("name") == target), None)
    if not stage:
        return target
    group = (stage.get("parallel_group") or "").strip()
    if group and target not in {"intake", "done"}:
        return wave_node_name(group)
    return target


def _wave_next(stages: list[dict[str, Any]], last_member_name: str) -> str:
    """Next graph node after the last member of a parallel wave."""
    idx = next((i for i, s in enumerate(stages) if s["name"] == last_member_name), None)
    if idx is None:
        return "done"
    return _linear_next(stages, idx)


async def _mark_parallel_progress(
    initiative_id: str,
    *,
    stage: str,
    active: list[str] | None = None,
) -> None:
    try:
        from sortie_deck.orchestrator import get_orchestrator

        orch = get_orchestrator()
        ini = orch.get(initiative_id)
        if not ini:
            return
        ini.current_stage = stage
        meta = dict(ini.meta or {})
        if active:
            meta["active_parallel"] = list(active)
        else:
            meta.pop("active_parallel", None)
        ini.meta = meta
        orch.store.upsert(ini)
        await orch._emit(
            ini.id,
            {
                "type": "progress",
                "stage": stage,
                "initiative_id": ini.id,
                "active_parallel": list(active or []),
            },
        )
    except Exception:
        return


def build_graph_from_template(
    template: dict[str, Any],
    registry: ExecutorRegistry,
    artifact_store: ArtifactStore,
):
    stages: list[dict[str, Any]] = list(template.get("stages") or [])
    if not stages:
        raise ValueError("pipeline template has no stages")

    stage_by_name = {s["name"]: s for s in stages}
    stage_index = {s["name"]: i for i, s in enumerate(stages)}

    async def run_stage(state: PipelineState, stage: str) -> PipelineState:
        if state.get("stopped"):
            return {**state, "status": "stopped", "stage": stage}

        cfg = stage_by_name.get(stage, {"name": stage, "role": "product"})
        role = _role_id(str(cfg.get("role", "product")))
        executor_name = _executor_name(stage, role.value, state, cfg)
        executor = registry.get(executor_name)
        artifact_dir = str(artifact_store.initiative_dir(state["initiative_id"]) / stage)

        upstream_paths = state.get("upstream", {})
        upstream_content: dict[str, str] = {}
        for kind, rel in upstream_paths.items():
            try:
                upstream_content[kind] = artifact_store.read_text(rel)
            except FileNotFoundError:
                upstream_content[kind] = ""

        role_personas = state.get("role_personas") or {}
        role_toolkits = state.get("role_toolkits") or {}
        stage_toolkits = state.get("stage_toolkits") or {}
        toolkit_briefs = state.get("toolkit_briefs") or {}
        persona = role_personas.get(role.value) or load_persona(role.value)
        toolkit_ids = list(stage_toolkits.get(stage) or role_toolkits.get(role.value) or [])
        toolkit_brief = (
            toolkit_briefs.get(f"stage:{stage}")
            or toolkit_briefs.get(f"role:{role.value}")
            or ""
        )
        if toolkit_brief and toolkit_brief not in persona:
            persona = f"{persona}\n\n{toolkit_brief}"

        # Agent-driven upstream/downstream consult before executing the node
        consult_artifacts: dict[str, str] = {}
        try:
            from sortie_deck.models import ActorKind
            from sortie_deck.orchestrator import get_orchestrator
            from sortie_deck.stage_consult import run_stage_consult

            orch = get_orchestrator()
            ini = orch.get(state["initiative_id"])
            if ini and stage not in {"intake", "done"}:
                role_titles = {
                    (r.role.value if hasattr(r.role, "value") else str(r.role)): r.title
                    for r in ini.roles
                }

                async def _post(
                    initiative_id: str,
                    *,
                    text: str,
                    actor_kind: str,
                    actor_name: str,
                    role: str | None = None,
                    msg_type: str = "chat",
                    meta: dict | None = None,
                ):
                    kind = (
                        ActorKind.AGENT
                        if actor_kind == "agent"
                        else ActorKind.SYSTEM
                        if actor_kind == "system"
                        else ActorKind.HUMAN
                    )
                    return await orch._post_room(
                        initiative_id,
                        text=text,
                        actor_kind=kind,
                        actor_name=actor_name,
                        role=role,
                        msg_type=msg_type,
                        meta=meta,
                    )

                async def _reply(to_role: str, question: str) -> str:
                    target = next(
                        (
                            r
                            for r in ini.roles
                            if (r.role.value if hasattr(r.role, "value") else str(r.role)) == to_role
                        ),
                        None,
                    )
                    if not target:
                        return "（编制中无此角色，跳过）"
                    return await orch._discussion_reply(
                        ini, target, question, role_titles.get(role.value, role.value)
                    )

                consult_artifacts = await run_stage_consult(
                    ini=ini,
                    initiative_id=ini.id,
                    stage=stage,
                    role=role.value,
                    brief=state["brief"],
                    upstream=upstream_content,
                    role_titles=role_titles,
                    post_room=_post,
                    reply_as_role=_reply,
                )
                if consult_artifacts:
                    from sortie_deck.models import TimelineEvent

                    events_pre = list(state.get("events") or [])
                    events_pre.append(
                        {
                            "stage": stage,
                            "role": role.value,
                            "kind": "consult",
                            "message": "Upstream/downstream consult completed",
                            "data": {"files": list(consult_artifacts.keys())},
                        }
                    )
                    state = {**state, "events": events_pre}
                    orch._append_timeline(
                        ini,
                        TimelineEvent(
                            stage=stage,
                            role=role.value,
                            kind="consult",
                            message="上下游确认沟通已完成",
                            data={"files": list(consult_artifacts.keys())},
                        ),
                    )
                    orch.store.upsert(ini)
        except Exception:
            consult_artifacts = {}

        ctx = StageContext(
            initiative_id=state["initiative_id"],
            thread_id=state["thread_id"],
            stage=stage,
            role=role,
            brief=state["brief"],
            human_instruction=state.get("human_instruction"),
            artifact_dir=artifact_dir,
            workspace_dir=state.get("workspace_dir"),
            upstream_artifacts=upstream_content,
            persona=persona,
            permissions={
                "qa_attempt": state.get("qa_attempt", 1),
                **_coding_perm_from_instruction(state.get("human_instruction")),
            },
            toolkit_ids=toolkit_ids,
            toolkit_brief=toolkit_brief,
        )

        async def _execute() -> StageResult:
            return await executor.run(ctx)

        from sortie_deck.settings import settings as _settings

        timeout = float(getattr(_settings, "stage_timeout_seconds", 900) or 900)

        async def _execute_with_timeout() -> StageResult:
            try:
                return await asyncio.wait_for(_execute(), timeout=timeout)
            except TimeoutError:
                return StageResult(
                    status="fail",
                    message=f"stage `{stage}` timed out after {timeout:.0f}s",
                    artifacts={},
                    proposed_next=stage,
                    meta={"timeout": True, "timeout_seconds": timeout},
                )

        if stage in ENG_BUILD_STAGES:
            result = await ENG_QUEUE.run(_execute_with_timeout)
        else:
            result = await _execute_with_timeout()

        written: dict[str, str] = dict(upstream_paths)
        for filename, content in {**consult_artifacts, **result.artifacts}.items():
            ref = artifact_store.write_text(state["initiative_id"], stage, filename, content)
            written[filename] = ref.path

        validate_stage_artifacts(stage, result.artifacts)

        events = list(state.get("events") or [])
        events.append(
            {
                "stage": stage,
                "role": role.value,
                "kind": "info",
                "message": result.message,
                "executor": executor_name,
                "status": result.status,
                "qa_attempt": state.get("qa_attempt"),
                "data": {
                    "executor": executor_name,
                    "status": result.status,
                    "qa_attempt": state.get("qa_attempt"),
                    "meta": result.meta or {},
                },
            }
        )

        return {
            **state,
            "stage": stage,
            "last_result": result.model_dump(mode="json"),
            "upstream": written,
            "events": events,
            "status": "running",
            "human_instruction": None,
        }

    def make_stage_node(stage_name: str):
        async def node(state: PipelineState) -> PipelineState | Command:
            if stage_name == "qa_verify":
                attempt = int(state.get("qa_attempt", 1))
                st = await run_stage({**state, "qa_attempt": attempt}, stage_name)
                st["qa_attempt"] = attempt + 1
            else:
                st = await run_stage(state, stage_name)

            result = st.get("last_result") or {}
            if result.get("status") != "needs_hitl":
                return st

            # Coding / tool permission block → force HITL so Teams can prompt
            meta = result.get("meta") or {}
            payload = {
                "stage": stage_name,
                "prompt": result.get("message")
                or f"`{stage_name}` needs operator approval (permissions).",
                "message": result.get("message", ""),
                "artifacts": list((st.get("upstream") or {}).keys()),
                "allowed_actions": [a.value for a in HitlAction],
                "kind": "permission" if meta.get("permission_block") else "needs_hitl",
                "retry_permission_mode": meta.get("retry_permission_mode") or "bypassPermissions",
            }
            decision_raw = interrupt(payload)
            if isinstance(decision_raw, dict):
                raw = dict(decision_raw)
                if hasattr(raw.get("action"), "value"):
                    raw["action"] = raw["action"].value
                decision = HitlDecision.model_validate(raw)
            else:
                decision = HitlDecision(action=HitlAction.APPROVE)

            events = list(st.get("events") or [])
            events.append(
                {
                    "stage": stage_name,
                    "kind": "hitl",
                    "message": f"HITL {decision.action.value} (permission)",
                    "data": decision.model_dump(mode="json"),
                }
            )
            update: PipelineState = {**st, "events": events, "status": "running"}

            if decision.action == HitlAction.STOP:
                update["stopped"] = True
                update["status"] = "stopped"
                return Command(update=update, goto=END)

            if decision.action in {HitlAction.REJECT}:
                update["human_instruction"] = decision.instruction or "Rejected permission grant"
                return Command(update=update, goto=END)

            # approve / rewrite → retry same stage with elevated permission mode
            retry_mode = payload.get("retry_permission_mode") or "bypassPermissions"
            instr = decision.instruction or ""
            update["human_instruction"] = (
                f"{instr}\n[sortie:coding_permission_mode={retry_mode}]".strip()
            )
            return Command(update=update, goto=stage_name)

        return node

    async def done_node(state: PipelineState) -> PipelineState:
        events = list(state.get("events") or [])
        events.append({"stage": "done", "kind": "transition", "message": "Initiative completed"})
        return {**state, "stage": "done", "status": "done", "events": events}

    def make_hitl_gate(stage_name: str):
        cfg = stage_by_name[stage_name]
        group = (cfg.get("parallel_group") or "").strip()
        if group:
            members = [s for s in stages if (s.get("parallel_group") or "").strip() == group]
            last = members[-1]["name"] if members else stage_name
            approve_next = _wave_next(stages, last)
        else:
            idx = stage_index[stage_name]
            approve_next = _linear_next(stages, idx)
        on_reject = _resolve_goto(stages, cfg.get("on_reject") or stage_name)
        on_fail = _resolve_goto(stages, cfg.get("on_fail") or on_reject)

        async def hitl_gate(state: PipelineState) -> Command:
            stage = state.get("stage", stage_name)
            result = state.get("last_result") or {}
            payload = {
                "stage": stage,
                "prompt": f"Review outputs of `{stage}` and choose an action.",
                "message": result.get("message", ""),
                "artifacts": list((state.get("upstream") or {}).keys()),
                "allowed_actions": [a.value for a in HitlAction],
            }
            decision_raw = interrupt(payload)
            if isinstance(decision_raw, dict):
                raw = dict(decision_raw)
                if hasattr(raw.get("action"), "value"):
                    raw["action"] = raw["action"].value
                decision = HitlDecision.model_validate(raw)
            else:
                decision = HitlDecision(action=HitlAction.APPROVE)

            events = list(state.get("events") or [])
            events.append(
                {
                    "stage": stage,
                    "kind": "hitl",
                    "message": f"HITL {decision.action.value}",
                    "data": decision.model_dump(mode="json"),
                }
            )
            update: PipelineState = {
                **state,
                "events": events,
                "hitl_decision": decision.model_dump(mode="json"),
                "status": "running",
            }

            if decision.action == HitlAction.STOP:
                update["stopped"] = True
                update["status"] = "stopped"
                return Command(update=update, goto=END)

            if decision.action == HitlAction.EDIT_INSTRUCTION:
                update["human_instruction"] = decision.instruction
                return Command(update=update, goto=stage)

            if decision.action == HitlAction.REJECT:
                update["human_instruction"] = decision.instruction or "Rejected — revise"
                return Command(update=update, goto=on_reject)

            if decision.action == HitlAction.REROUTE and decision.next_stage:
                return Command(update=update, goto=_resolve_goto(stages, decision.next_stage))

            # approve
            if stage == "qa_verify" and not bool(result.get("qa_passed")):
                return Command(update=update, goto=on_fail)
            return Command(update=update, goto=approve_next)

        return hitl_gate

    def make_wave_node(group: str, members: list[dict[str, Any]]):
        from sortie_deck.parallel import group_wave_branches

        member_names = [m["name"] for m in members]
        branches = group_wave_branches(members)

        async def wave(state: PipelineState) -> PipelineState | Command:
            if state.get("stopped"):
                return {**state, "status": "stopped"}

            initiative_id = state["initiative_id"]
            await _mark_parallel_progress(initiative_id, stage=member_names[0], active=member_names)

            async def _run_branch(branch_members: list[dict[str, Any]]) -> PipelineState:
                st: PipelineState = dict(state)
                for m in branch_members:
                    name = m["name"]
                    await _mark_parallel_progress(initiative_id, stage=name, active=member_names)
                    st = await run_stage(dict(st), name)
                    if (st.get("last_result") or {}).get("status") == "needs_hitl":
                        return st
                    if st.get("stopped"):
                        return st
                return st

            results = await asyncio.gather(*[_run_branch(br["members"]) for br in branches])

            merged_upstream = dict(state.get("upstream") or {})
            merged_events = list(state.get("events") or [])
            last_result: dict[str, Any] = {}
            hitl_member: str | None = None
            hitl_state: PipelineState | None = None

            for br, st in zip(branches, results, strict=True):
                up = dict(st.get("upstream") or {})
                # Bare kind keys: last-wins (fine for trunk artifacts shared into later stages).
                for kind, rel in up.items():
                    if "::" in str(kind):
                        continue
                    merged_upstream[kind] = rel
                # Stage-scoped copies so parallel members don't clobber each other in the
                # initiative artifact index (implementation.md from eng_web vs eng_backend).
                for m in br["members"]:
                    name = m["name"]
                    for kind, rel in up.items():
                        if "::" in str(kind):
                            continue
                        rel_n = str(rel).replace("\\", "/")
                        if f"/{name}/" in f"/{rel_n}/":
                            merged_upstream[f"{name}::{kind}"] = rel
                for ev in st.get("events") or []:
                    if ev not in merged_events:
                        merged_events.append(ev)
                last_result = st.get("last_result") or last_result
                if (st.get("last_result") or {}).get("status") == "needs_hitl" and hitl_member is None:
                    hitl_member = st.get("stage") or br["members"][-1]["name"]
                    hitl_state = st

            tip = branches[-1]["members"][-1]["name"] if branches else member_names[-1]
            await _mark_parallel_progress(initiative_id, stage=tip, active=None)

            base: PipelineState = {
                **state,
                "stage": tip,
                "upstream": merged_upstream,
                "events": merged_events,
                "last_result": last_result,
                "status": "running",
                "human_instruction": None,
            }
            branch_summary = " ∥ ".join(
                "→".join(m["name"] for m in br["members"]) for br in branches
            )
            base["events"] = list(merged_events) + [
                {
                    "stage": tip,
                    "kind": "transition",
                    "message": f"Parallel wave `{group}` finished: {branch_summary}",
                    "data": {
                        "parallel_group": group,
                        "members": member_names,
                        "branches": [
                            {"id": br["id"], "members": [m["name"] for m in br["members"]]}
                            for br in branches
                        ],
                    },
                }
            ]

            if hitl_member and hitl_state is not None:
                # Re-enter the blocked member for permission HITL (single-branch resume)
                result = hitl_state.get("last_result") or {}
                meta = result.get("meta") or {}
                payload = {
                    "stage": hitl_member,
                    "prompt": result.get("message")
                    or f"`{hitl_member}` needs operator approval (permissions).",
                    "message": result.get("message", ""),
                    "artifacts": list(merged_upstream.keys()),
                    "allowed_actions": [a.value for a in HitlAction],
                    "kind": "permission" if meta.get("permission_block") else "needs_hitl",
                    "retry_permission_mode": meta.get("retry_permission_mode") or "bypassPermissions",
                    "parallel_group": group,
                    "parallel_members": member_names,
                }
                decision_raw = interrupt(payload)
                if isinstance(decision_raw, dict):
                    raw = dict(decision_raw)
                    if hasattr(raw.get("action"), "value"):
                        raw["action"] = raw["action"].value
                    decision = HitlDecision.model_validate(raw)
                else:
                    decision = HitlDecision(action=HitlAction.APPROVE)
                if decision.action == HitlAction.STOP:
                    return Command(
                        update={**base, "stopped": True, "status": "stopped"},
                        goto=END,
                    )
                if decision.action == HitlAction.REJECT:
                    return Command(
                        update={
                            **base,
                            "human_instruction": decision.instruction or "Rejected permission grant",
                            "status": "stopped",
                            "stopped": True,
                        },
                        goto=END,
                    )
                retry_mode = payload.get("retry_permission_mode") or "bypassPermissions"
                instr = decision.instruction or ""
                return Command(
                    update={
                        **base,
                        "human_instruction": (
                            f"{instr}\n[sortie:coding_permission_mode={retry_mode}]".strip()
                        ),
                    },
                    goto=wave_node_name(group),
                )

            return base

        return wave

    graph = StateGraph(PipelineState)
    waves = collapse_to_waves(stages)

    # Register nodes
    registered: set[str] = set()
    for wave in waves:
        if wave["kind"] == "single":
            s = wave["stage"]
            name = s["name"]
            if name == "done":
                graph.add_node("done", done_node)
                registered.add("done")
                continue
            graph.add_node(name, make_stage_node(name))
            registered.add(name)
            if s.get("hitl_after"):
                graph.add_node(f"hitl__{name}", make_hitl_gate(name))
                registered.add(f"hitl__{name}")
        else:
            group = wave["group"]
            members = wave["members"]
            wname = wave_node_name(group)
            graph.add_node(wname, make_wave_node(group, members))
            registered.add(wname)
            # Keep individual stage nodes for HITL / inspect resume targets
            for m in members:
                mname = m["name"]
                if mname not in registered:
                    graph.add_node(mname, make_stage_node(mname))
                    registered.add(mname)

    # Edges across waves
    first_wave = waves[0]
    if first_wave["kind"] == "single":
        graph.add_edge(START, first_wave["stage"]["name"])
    else:
        graph.add_edge(START, wave_node_name(first_wave["group"]))

    for wi, wave in enumerate(waves):
        if wave["kind"] == "single":
            s = wave["stage"]
            name = s["name"]
            if name == "done":
                graph.add_edge("done", END)
                continue
            # Next entry
            if wi + 1 >= len(waves):
                nxt = "done"
            else:
                nw = waves[wi + 1]
                nxt = (
                    nw["stage"]["name"]
                    if nw["kind"] == "single"
                    else wave_node_name(nw["group"])
                )
            if s.get("hitl_after"):
                graph.add_edge(name, f"hitl__{name}")
            else:
                graph.add_edge(name, nxt)
        else:
            group = wave["group"]
            wname = wave_node_name(group)
            last = wave["members"][-1]["name"]
            if wi + 1 >= len(waves):
                nxt = "done"
            else:
                nw = waves[wi + 1]
                nxt = (
                    nw["stage"]["name"]
                    if nw["kind"] == "single"
                    else wave_node_name(nw["group"])
                )
            # If catalog still marked hitl on last member, route via its gate
            if wave["members"][-1].get("hitl_after"):
                gate = f"hitl__{last}"
                if gate not in registered:
                    graph.add_node(gate, make_hitl_gate(last))
                    registered.add(gate)
                graph.add_edge(wname, gate)
            else:
                graph.add_edge(wname, nxt)

    return graph


def build_graph(registry: ExecutorRegistry, artifact_store: ArtifactStore, template_name: str = "default"):
    tpl = load_pipeline_template(template_name)
    return build_graph_from_template(tpl, registry, artifact_store)


async def compile_pipeline(
    registry: ExecutorRegistry,
    artifact_store: ArtifactStore,
    checkpoint_path: Path,
    postgres_uri: str | None = None,
    template_name: str = "default",
):
    """Compile one graph; returns (compiled, resources)."""
    graphs, resources = await compile_pipelines(
        registry,
        artifact_store,
        checkpoint_path,
        postgres_uri=postgres_uri,
        tracks=[template_name],
    )
    return graphs[template_name], resources


async def compile_pipelines(
    registry: ExecutorRegistry,
    artifact_store: ArtifactStore,
    checkpoint_path: Path,
    postgres_uri: str | None = None,
    tracks: list[str] | None = None,
) -> tuple[dict[str, Any], dict]:
    """Compile multiple track graphs sharing one checkpointer."""
    import aiosqlite

    track_list = tracks or ["default", "express", "standard"]
    resources: dict = {}
    saver = None

    if postgres_uri:
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            cm = AsyncPostgresSaver.from_conn_string(postgres_uri)
            saver = await cm.__aenter__()
            await saver.setup()
            resources["cm"] = cm
            resources["saver"] = saver
        except Exception:
            saver = None

    if saver is None:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(str(checkpoint_path))
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL;")
        saver = AsyncSqliteSaver(conn)
        await saver.setup()
        resources["conn"] = conn
        resources["saver"] = saver

    graphs: dict[str, Any] = {}
    for track in track_list:
        builder = build_graph(registry, artifact_store, track)
        graphs[track] = builder.compile(checkpointer=saver)
    return graphs, resources
