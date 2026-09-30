# Goals & non-goals

## Problem

Office software delivery still runs on human relays: PRDs in chat, verbal API deals, integration by luck. Sortie Deck turns that chain into a **confirmable mission control plane**: role agents run stages, artifacts hand off by contract, and humans stay at the gates.

## Goals

- **Mission-centric** — one sortie = startable pipeline + squad room + artifact tree.
- **Contracted collaboration** — stages emit named files; downstream reads files, not paste.
- **Confirmable pipelines** — planner proposes → human confirms/edits → then compile LangGraph.
- **Pluggable execution** — mock / Claude Code / Cursor CLI / deploy shell share one orchestration.
- **HITL by default** — interrupts, permission modes, and room confirmation — not a black box.

## Non-goals (today)

- Not a general-purpose agent chat product or IM replacement.
- Not a full Kubernetes / CRD workflow engine fork.
- Not reinventing enterprise vector search in-repo (WeKnora is optional).
- Not replacing LangGraph with a custom engine (see roadmap non-goals).
- Default persistence stays local-friendly (JSON / SQLite); multi-tenant cloud DBs are later.

## Success criteria

| Signal | Meaning |
|--------|---------|
| Demoable cold start | Full HITL sortie works on mock executors |
| Editable rails | Stages and parallel groups editable before confirm |
| Traceable artifacts | Per-stage dirs + contract checks |
| Docs build | `mkdocs build` succeeds |
