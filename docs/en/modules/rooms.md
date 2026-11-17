# Squad Rooms

## 1. Overview

Per-mission collaboration channel: join, chat, mentions, slash commands that drive the orchestrator.

| Item | Value |
|------|-------|
| Code | `rooms.py` + orchestrator room methods |
| Storage | `data/rooms/` |
| API | `/api/initiatives/{id}/squad/*` (aliases `/room/*`) |

## 2. Message model

```text
RoomMessage
  actor_kind: human | agent | system
  actor_name, role?, msg_type: chat|stage|hitl|decision|system
  text, meta
```

## 3. Commands

| Command | Effect |
|---------|--------|
| `/confirm` | `confirm_pipeline` |
| `/start` | `start_pipeline` (errors posted if unconfirmed) |
| `/approve` `/reject` `/rewrite` | HITL |
| `/stop` | stop |

Mentions `@product|design|eng|eng_ios|eng_android|eng_web|eng_backend|eng_agent|qa|deploy|all` trigger template discussion replies in draft (and when mentioned).

## 4. Critical path

Human post → parse command or discuss → persist message → SSE `room_message` → optional initiative update event.

## 5. Technical design (target)

- Discussion LLM with memory + toolkit brief
- Threads / reactions
- Bridge adapters (Feishu/Slack) mapping to same command set

## 6. Development plan

### P0 (2 days)

| Task | Acceptance |
|------|------------|
| In-UI command help | copy lists commands |
| `/confirm` documented in i18n placeholder | done |
| Test discuss + confirm + start via messages | pytest |

### P1 (1 week)

| Task | Acceptance |
|------|------------|
| LLM discuss behind flag | fallback templates |
| Attach artifact snippets on stage messages | clickable in UI |

### P2 (2 weeks)

| Task | Acceptance |
|------|------------|
| Feishu/Slack webhook bridge | map /approve |
| Presence indicators | optional |

## 7. Dependencies

- Orchestrator lifecycle, Web chat panel, Auth identity for author_name
