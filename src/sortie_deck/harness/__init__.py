"""Sortie Deck shared agent harness — plan → tool loop → confirm gates.

Inspired by AWS Strands / AgentCore harness ideas:
- one agent loop with tools, turn limits, and intercept hooks
- human confirmation before irreversible acts
- product-wide reuse (mission briefing, room agents, etc.)

This is Sortie Deck's thin in-process harness — not a vendor SDK dependency.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from sortie_deck.models import utc_now


class EventKind(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    THINK = "think"
    TOOL = "tool"
    PLAN = "plan"
    CONFIRM = "confirm"
    WATERFALL = "waterfall"
    SYSTEM = "system"
    ERROR = "error"
    DONE = "done"


class HarnessEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"hev_{uuid4().hex[:10]}")
    kind: EventKind
    text: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    at: str = Field(default_factory=lambda: utc_now().isoformat())


class ToolResult(BaseModel):
    ok: bool = True
    summary: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


ToolHandler = Callable[[dict[str, Any]], Awaitable[ToolResult] | ToolResult]


@dataclass
class ToolSpec:
    name: str
    description: str
    handler: ToolHandler
    # If True, tool may only run after human confirmed pending plan
    requires_confirm: bool = False


@dataclass
class HarnessState:
    session_id: str
    goal: str = ""
    messages: list[dict[str, str]] = field(default_factory=list)
    events: list[HarnessEvent] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    pending_confirm: dict[str, Any] | None = None
    status: Literal["idle", "planning", "awaiting_confirm", "running", "done", "failed"] = "idle"
    turn: int = 0


def new_session_id() -> str:
    return f"brf_{uuid4().hex[:12]}"


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(name)
        return self._tools[name]

    def list(self) -> list[ToolSpec]:
        return list(self._tools.values())


class Harness:
    """Shared agent loop: emit waterfall events, call tools, gate on confirm."""

    def __init__(
        self,
        tools: ToolRegistry,
        *,
        max_turns: int = 8,
        name: str = "sortie-harness",
    ) -> None:
        self.tools = tools
        self.max_turns = max_turns
        self.name = name

    def emit(self, state: HarnessState, kind: EventKind, text: str = "", **data: Any) -> HarnessEvent:
        ev = HarnessEvent(kind=kind, text=text, data=data)
        state.events.append(ev)
        return ev

    async def call_tool(
        self,
        state: HarnessState,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ToolResult:
        spec = self.tools.get(name)
        if spec.requires_confirm and state.status != "awaiting_confirm" and not state.context.get(
            "confirmed"
        ):
            return ToolResult(ok=False, summary=f"tool `{name}` requires confirmation first")
        args = args or {}
        self.emit(state, EventKind.TOOL, f"→ {name}", tool=name, args=args, phase="start")
        try:
            result = spec.handler(args)
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[misc]
            assert isinstance(result, ToolResult)
        except Exception as exc:  # noqa: BLE001
            result = ToolResult(ok=False, summary=str(exc), data={"error": str(exc)})
        self.emit(
            state,
            EventKind.TOOL,
            result.summary or f"← {name}",
            tool=name,
            ok=result.ok,
            phase="end",
            result=result.data,
        )
        return result

    def request_confirm(self, state: HarnessState, *, title: str, plan: dict[str, Any]) -> None:
        state.pending_confirm = {"title": title, "plan": plan}
        state.status = "awaiting_confirm"
        self.emit(state, EventKind.CONFIRM, title, plan=plan)

    def confirm(self, state: HarnessState, *, approved: bool, note: str = "") -> None:
        if approved:
            state.context["confirmed"] = True
            state.context["confirm_note"] = note
            state.status = "running"
            self.emit(state, EventKind.SYSTEM, note or "规划已确认，继续执行")
        else:
            state.context["confirmed"] = False
            state.pending_confirm = None
            state.status = "planning"
            self.emit(state, EventKind.SYSTEM, note or "已驳回，请继续调整规划")
