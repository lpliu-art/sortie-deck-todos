# Agent Harness

## 1. Overview

Shared in-process agent loop for Sortie Deck — inspired by AWS **Strands / AgentCore harness** ideas
(tools, turn limits, confirm gates, waterfall traces), without taking a vendor SDK dependency.

| Item | Value |
|------|-------|
| Code | `harness/__init__.py` |
| First consumer | `mission_briefing.py` (create-squad chat) |
| API | `/api/briefing/sessions` |

## 2. Loop

```text
user message
  → tools (history / KB / pipeline / loadout / ensure roles)
  → waterfall events
  → CONFIRM gate
  → irreversible act (create initiative)
```

## 3. Reuse

Use the same `Harness` + `ToolRegistry` for room agents, toolkit MCP acts, and future flows
that need plan → confirm → act.
