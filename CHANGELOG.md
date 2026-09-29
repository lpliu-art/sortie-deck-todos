# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Apache-2.0 license and open-source project docs (EN/ZH README, MkDocs Material i18n site)
- Architecture overview, data-flow diagrams, and per-module technical + implementation plans
- Expanded per-module specs (entry → core → platform) with API contracts, sequences, P0–P2 task tables and acceptance criteria
- GitHub CI (`ruff` / `pytest` / workbench `tsc` / `mkdocs`), Issue & PR templates
- `TDT_TOKEN_SECRET` / `TDT_ENV` auth hardening, artifact path traversal guards
- Workbench extracts: `api` client, `OperatorChip`, `PipelineEditor`
- Toolkit examples under `packages/examples/`; executor soft-fail when CLI missing
- P1: `TDT_STORAGE=sqlite` initiative repository, optional LLM planner / room LLM / MCP runtime flags
- P2: sqlite run queue + leases, S3 artifact backend, org policy, Slack/Feishu bridges, `sortie_deck.executors` entry points

### Changed

- Product rename: **Rally** → **Sortie Deck**; Python package `trusted-dev-teams` → `sortie-deck` (`sortie_deck`); CLI `sortie` (legacy `tdt` alias); legacy `rally_*` storage keys / `rally.executors` still accepted
- Orchestrator `startup()` recompiles confirmed custom graphs for HITL resume after restart
- Structured API error `pipeline_not_confirmed` when starting an unconfirmed mission

## [0.1.0] — 2026-09-23

### Added

- FastAPI control plane with LangGraph pipelines (express / standard / default tracks)
- Pipeline planner agent with human confirm and manual stage editing
- Squad rooms, HITL slash commands, SSE progress
- Auth & RBAC, knowledge (Codex), memory, agent forge, toolkit (Tools / MCP / Skills)
- React TypeScript workbench (Signal Deck) with CN/EN UI and themes
- CLI: `sortie smoke`, `sortie api`
- Pluggable executors: mock, Claude Code, Cursor CLI, deploy shell

[Unreleased]: https://github.com/Truested-Dev-Teams/Truested-Dev-Teams/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Truested-Dev-Teams/Truested-Dev-Teams/releases/tag/v0.1.0
