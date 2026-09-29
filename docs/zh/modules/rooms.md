# 小队频道

## 1. 概述

按任务的协作频道：加入、聊天、点名、驱动编排器的斜杠命令。

| 项 | 值 |
|----|-----|
| 代码 | `rooms.py` + 编排器房间方法 |
| 存储 | `data/rooms/` |
| API | `/squad/*`（别名 `/room/*`） |

## 2. 消息模型

```text
RoomMessage
  actor_kind: human | agent | system
  msg_type: chat|stage|hitl|decision|system
```

## 3. 命令

| 命令 | 效果 |
|------|------|
| `/confirm` | 确认航线 |
| `/start` | 出击（未确认则频道报错） |
| `/approve` `/reject` `/rewrite` | HITL |
| `/stop` | 停止 |

`@product|design|eng|eng_ios|eng_android|eng_web|eng_backend|eng_agent|qa|deploy|all` 触发模板讨论回复。

## 4. 关键路径

发帖 → 解析命令或讨论 → 落库 → SSE → 可选任务更新事件。

## 5. 技术方案（目标）

- 带记忆/工具的讨论 LLM
- 回复串 / 表情
- 飞书/Slack 桥，映射同一命令集

## 6. 开发计划

### P0（2 天）

| 任务 | 验收 |
|------|------|
| UI 命令帮助 | 文案列出命令 |
| i18n 占位含 `/confirm` | 完成 |
| 消息路径测 discuss+confirm+start | pytest |

### P1（1 周）

| 任务 | 验收 |
|------|------|
| 讨论 LLM + 开关 | 失败回落模板 |
| 阶段消息挂产物摘要 | UI 可点 |

### P2（2 周）

| 任务 | 验收 |
|------|------|
| 飞书/Slack webhook | 映射 /approve |
| 在线态 | 可选 |

## 7. 依赖

- 编排生命周期、Web 聊天、Auth 显示名
