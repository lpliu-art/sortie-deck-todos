# Contributing

Thanks for contributing to **Sortie Deck**.

## Development setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
cd apps/web && npm install
```

## Checks before PR

```bash
# Python
ruff check src tests
pytest -q

# Workbench
cd apps/web && npx tsc --noEmit

# Docs
mkdocs build --strict
```

## Web manual smoke (apps/web)

After UI refactors, run through once against a local backend:

1. **Login** — sign in; header shows operator chip (avatar, name, role).
2. **Create** — new task from Tasks; open squad room.
3. **Confirm pipeline** — on a draft initiative, review stages; confirm (or edit → save → confirm).
4. **Start** — start pipeline; status moves off draft and rail updates.

## Guidelines

1. Prefer small, focused PRs.
2. Add or update tests for control-plane behavior.
3. Keep EN/ZH docs in sync when changing architecture or modules.
4. Do not commit secrets, local `data/` dumps, or personal `.env`.
5. Follow the Code of Conduct in the repository root (`CODE_OF_CONDUCT.md`).

## Document languages

- README: `README.md` (EN) + `README.zh-CN.md` (ZH)
- Site: `docs/en/` + `docs/zh/` with MkDocs language switcher

## License

By contributing, you agree your contributions are licensed under Apache-2.0.
