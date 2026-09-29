---
name: knowledge-for-cursor
description: Retrieve enterprise knowledge (WeKnora) for the current mission and load a pack into Cursor (.cursor/rules)
---

# Knowledge for Cursor

**Enterprise KB** = [WeKnora](https://github.com/Tencent/WeKnora) (腾讯开源).  
Sortie Deck only **imports** and **catalogs** documents; **retrieval** uses WeKnora hybrid-search.  
**Cursor** is the coding executor — not the knowledge store.

## Configure

```bash
export TDT_KB_BACKEND=weknora
export TDT_WEKNORA_BASE_URL=http://127.0.0.1:8080
export TDT_WEKNORA_API_KEY=...
export TDT_WEKNORA_KB_ID=...
```

Without WeKnora, Sortie Deck falls back to the local catalog keyword match (dev only).

## When to use

- Before `cursor_cli` implements a stage.
- Operator: `sortie knowledge pack --brief "…" --workspace .`
- Import: `sortie knowledge import --title "…" --body "…" --folder /产品`
- Sync catalog: `sortie knowledge sync`

## What it does

1. Call WeKnora `POST /api/v1/knowledge-bases/{id}/hybrid-search` (or local fallback).
2. Write:
   - `.cursor/rules/sortie-knowledge.mdc` — always-apply rule
   - `.sortie-deck/knowledge-pack.md` — full pack
3. Cursor treats the pack as authoritative product / API / design context.

## Sortie Deck scope (non-goals)

| Sortie Deck does | WeKnora does |
|------------|--------------|
| Import (file / URL / Markdown) | Parse / embed / index |
| Catalog + folder mirror | Hybrid / vector / keyword retrieve |
| Sync directory listing | Graph / FAQ / Wiki QA |
