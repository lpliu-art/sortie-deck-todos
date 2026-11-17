# ADR-0002 · Pipeline specs before compiled graphs

## Status

Accepted — 2026-03

## Context

Fixed templates cannot cover dynamic sorties (multi-surface parallel, forked self-test, integrate). Editing graph code is hard for humans to confirm.

## Decision

Treat editable **`pipeline_specs`** (`branch` / `parallel_group` / `depends_on`) as the human confirmation surface:

1. Planner proposes → 2. Human confirms → 3. Materialize + compile

The workbench rail and runtime share the same spec source.

## Consequences

- Specs are the source of truth; graphs are derived.
- Must maintain planner (heuristic / LLM) and validation.
- Parallel semantics live in `parallel.py`.

## Alternatives

Static YAML-only templates, or pure NL recompile each time — either lacks dynamism or auditable structure.
