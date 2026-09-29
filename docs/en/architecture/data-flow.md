# Data Flow

## Mission lifecycle

```mermaid
sequenceDiagram
  participant User
  participant Planner as PipelinePlanner
  participant Orch as Orchestrator
  participant Graph as LangGraph

  User->>Orch: create_initiative
  Orch->>Planner: plan_pipeline
  Planner-->>User: proposal_pending
  User->>Orch: edit_or_confirm_pipeline
  User->>Orch: start_pipeline
  Orch->>Graph: astream_custom_graph
  Graph-->>User: HITL_interrupt
  User->>Orch: approve_reject_rewrite
  Graph-->>User: done_artifacts
```

## Artifact handoff

1. A stage executor returns `StageResult.artifacts` (filename → content).
2. `ArtifactStore` writes under `data/artifacts/<initiative>/<stage>/`.
3. Paths accumulate in graph state `upstream`; later stages read text via `StageContext.upstream_artifacts`.
4. Contracts in `contracts.REQUIRED` validate required filenames per stage.

## Realtime

- `GET /api/initiatives/{id}/events` — SSE for progress / HITL / room messages.
- Room messages persist under `data/rooms/` via `RoomStore`.

## Checkpoints

LangGraph checkpointer (SQLite by default, optional Postgres) stores thread state keyed by initiative `thread_id`, so HITL resume survives process restart when the same checkpoint DB is reused.
