# ADR-0003 · Optional decisioner (TypeSafe Jev)

## Status

Proposed — see [TODO.md](../../../../TODO.md)

## Context

HITL needs suggestions / structured decisions without binding pause semantics to one vendor.

## Decision (direction)

- **Jev System One (typesafe.ai)** as an optional decisioner mount: suggested actions + rationale.
- **LangGraph `interrupt()` remains the only pause truth**; Jev does not replace gates.
- On failure, degrade to pure human HITL.

## Consequences

- Clear boundary: suggestion ≠ auto-approve.
- Docs/topics can stress “HITL + optional decisioner”.
- Stay Proposed until implemented — no empty promises.

## Alternatives

Built-in rules engine, or UI-only buttons as the default path.
