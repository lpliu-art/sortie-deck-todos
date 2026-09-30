# ADR-0001 · LangGraph for sortie orchestration

## Status

Accepted — 2026-03

## Context

We need a pausable, resumable, branch-aware sortie runtime that aligns with workbench HITL.

## Decision

Use **LangGraph** `StateGraph` + checkpointer:

- Nodes = pipeline stages (or parallel waves)
- `interrupt()` = human-in-the-loop pause
- `Command` = resume / rewrite / reroute
- Compile per mission as `custom:{initiative_id}`

## Consequences

- Tied to LangGraph semantics/versions; parallelism via wave nodes rather than a free DAG scheduler.
- HITL payload shapes evolve with the UI contract.
- Tests focus on wave / interrupt behavior (`tests/test_parallel_waves.py`).

## Alternatives

Homegrown state machine, Temporal, or pure asyncio DAG — poorer fit for existing HITL / artifact contracts.
