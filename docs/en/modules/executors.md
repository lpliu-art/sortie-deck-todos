# Executors & Plugins

## 1. Overview

Stage runners that turn `StageContext` into `StageResult` artifacts. Coding/deploy providers are swappable.

| Item | Value |
|------|-------|
| Registry | `registry.py`, `plugins/factory.py` |
| Queue | `plugins/queue.py` (`ENG_QUEUE`) |
| Impl | `mock.py`, `coding.py`, `deploy.py` |

## 2. Protocol

```python
async def run(self, ctx: StageContext) -> StageResult:
    # returns status, message, artifacts{filename: content}, qa_passed?, proposed_next?
```

`StageContext` includes: brief, persona (+ toolkit brief), upstream artifact texts, workspace_dir, permissions.

## 3. Built-ins

| Name | Stage use | Notes |
|------|-----------|-------|
| `mock_intake` / `mock_product` / `mock_eng` / `mock_qa` / `mock_deploy` | demos | deterministic artifacts |
| `mock_qa_cases` / `mock_selftest` / `mock_integrate` / `mock_handoff` | standard track | |
| `claude_code` / `cursor_cli` | eng_implement | worktree under `data/worktrees` |
| `deploy_shell` | deploy | `TDT_DEPLOY_CMD` template |
| `llm_product` | optional PRD | needs LLM keys |

Resolution: template executor field, else role/stage heuristics in `graph._executor_name` (coding_executor / deploy_executor from state).

## 4. Technical design (target)

- Provider health: `probe()` → version/path
- Streaming logs → room `msg_type=stage`
- Sandbox profiles for shell (cwd allowlist, env scrub)
- Entry points: `sortie_deck.executors` pkg for community plugins

## 5. Development plan

### P0 (2–3 days)

| Task | Acceptance |
|------|------------|
| README section: env for Claude/Cursor | copy-paste works |
| Executor list test equals factory register | pytest |
| Fail soft when CLI missing | clear StageResult message |

### P1 (1–2 weeks)

| Task | Acceptance |
|------|------------|
| Log streaming hook | squad sees chunks |
| `probe()` on `/api/executors` | status field |
| MCP tool calls from coding executor | flag gated |

### P2 (2 weeks)

| Task | Acceptance |
|------|------------|
| Plugin discovery via entry points | load external |
| Resource limits (time/cpu) | enforced |

## 6. Test plan

- Mock contract satisfaction per stage
- Eng queue concurrency smoke
- Missing binary → non-crash

## 7. Dependencies

- Graph stage mapping, Toolkit briefs, Artifacts store, Settings
