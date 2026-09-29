# Contributing to Sortie Deck

Thank you for your interest in contributing to **Sortie Deck** (Sortie Deck / `sortie-deck`).

Full bilingual contributor guides live in the docs site:

- English: [docs/en/contributing.md](docs/en/contributing.md)
- 简体中文: [docs/zh/contributing.md](docs/zh/contributing.md)

## Quick path

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
pytest -q
cd apps/web && npm install && npx tsc --noEmit
mkdocs build --strict
```

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md).

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
