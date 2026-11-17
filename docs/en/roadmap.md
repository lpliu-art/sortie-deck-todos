# Roadmap

Cross-cutting milestones for Sortie Deck as an open-source control plane.

Per-module detailed plans (tasks, acceptance, estimates) live under [Modules](modules/auth.md).

## Suggested delivery order

1. **Entry**: [Auth](modules/auth.md) → [Web](modules/web.md) → [CLI](modules/cli.md)
2. **Core loop**: [Orchestrator](modules/orchestrator.md) → [Pipeline](modules/pipeline.md) → [Graph](modules/graph.md) → [Rooms](modules/rooms.md)
3. **Platform**: [Executors](modules/executors.md) → [Toolkit](modules/toolkit.md) → [Agents](modules/agents.md) → [Knowledge](modules/knowledge.md) / [Memory](modules/memory.md) → [Artifacts](modules/artifacts.md)

## P0 — OSS hardening

- CI: lint (`ruff`), pytest, workbench `tsc`, `mkdocs build`
- Security review of auth tokens, artifact path traversal, toolkit imports
- Example `.env.example` and executor setup guides
- Issue / PR templates

## P1 — Storage & planner

- [x] SQL-backed repositories behind existing store interfaces (`TDT_STORAGE=sqlite`, initiatives)
- [x] Optional LLM pipeline planner (`TDT_PIPELINE_LLM`; human confirm still mandatory; heuristic fallback)
- [x] MCP runtime wired into coding executors (`TDT_MCP_RUNTIME`, stdio tools/list → prompt)
- [x] Discussion LLM for squad mentions (`TDT_ROOM_LLM`; template fallback)

## P2 — Production operators

- [x] Multi-worker run queue and locking (`TDT_RUN_BACKEND=sqlite` + leases)
- [x] S3-compatible artifacts (`TDT_ARTIFACT_BACKEND=s3`, optional `.[s3]`)
- [x] Org policies for tools / tracks (`TDT_ORG_POLICY_PATH`)
- [x] External chat bridges (`/api/bridges/slack`, `/api/bridges/feishu`)
- [x] Community executor packaging (`sortie_deck.executors` entry points + demo package)

## Non-goals (near term)

- Replacing LangGraph with a custom engine
- Shipping a closed SaaS-only core
