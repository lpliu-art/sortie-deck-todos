# Getting Started

## Requirements

- Python **3.12+**
- Node.js **18+** (workbench)
- Optional: Postgres (LangGraph checkpointer)

## Install

```bash
cd sortie-deck-todos
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Docs site:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Run

```bash
# Terminal 1 — API
sortie api
# http://127.0.0.1:8787/api/health

# Terminal 2 — Workbench
cd apps/web && npm install && npm run dev
# http://127.0.0.1:5173
```

Dev logins: `admin` / `admin123`, `operator` / `operator123`.

## Smoke CLI

```bash
sortie smoke
```

Auto-confirms the pipeline and drives HITL for a demo loop.

## First mission (UI)

1. Sign in → **Tasks** → create mission (brief + optional track hint / loadout).
2. Open **Squad** — read the **pipeline planner** proposal.
3. Edit stages if needed → **Confirm track** (or `/confirm`).
4. **Start sortie** (or `/start`).
5. Clear HITL gates with `/approve` / `/reject` / `/rewrite`.

## Next

- [Architecture](architecture/overview.md)
- [Pipeline Planner](modules/pipeline.md)
