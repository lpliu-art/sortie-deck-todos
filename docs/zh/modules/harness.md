# Agent Harness

## 1. 概述

Sortie Deck 进程内公用 Agent 循环，参考 AWS **Strands / AgentCore harness** 思想
（工具、轮次限制、确认门禁、瀑布流轨迹），不绑定厂商 SDK。

| 项 | 值 |
|----|-----|
| 代码 | `harness/__init__.py` |
| 首个消费者 | `mission_briefing.py`（对话建队） |
| API | `/api/briefing/sessions` |

## 2. 循环

```text
用户消息
  → 工具（历史 / 知识库 / 航线 / 编制 / 补角色）
  → 瀑布流事件
  → CONFIRM 门禁
  → 副作用（创建任务）
```

## 3. 复用

小队讨论、MCP 工具调用、后续「规划—确认—执行」流均可挂同一 `Harness`。
