# Artifacts & Store

## 1. Overview

Filesystem-backed artifact storage for stage outputs; initiative keeps `ArtifactRef` index; API serves file bytes.

| Item | Value |
|------|-------|
| Code | `artifacts.py` |
| Root | `data/artifacts/<initiative>/<stage>/` |
| API | `GET /api/initiatives/{id}/artifacts/{path}` |

## 2. Write path

Executor returns map → `ArtifactStore.write_text` → relative path into graph `upstream` → orchestrator `_sync_artifacts_from_upstream` appends refs.

## 3. Security requirements

- Prevent path traversal (`..`, absolute paths)
- Authorize artifact read only for authenticated users (optionally mission members later)
- Do not execute artifact contents

## 4. Technical design (target)

- Content-addressed blob store (`sha256`) + thin refs
- Diff API between qa attempts / eng loops
- S3-compatible backend via settings
- Signed short-lived download URLs

## 5. Development plan

### P0 (2 days)

| Task | Acceptance |
|------|------------|
| Path traversal tests | rejected |
| Auth required on download | 401 without token |
| Document layout on disk | this page |

### P1 (1 week)

| Task | Acceptance |
|------|------------|
| Diff two artifact versions | API + simple UI |
| Content hash in ArtifactRef.meta | stored |

### P2 (2 weeks)

| Task | Acceptance |
|------|------------|
| S3 backend | feature flag |
| Retention job | old missions pruned |

## 6. Dependencies

- Graph writes, Orchestrator sync, Web preview pane, Contracts filenames
