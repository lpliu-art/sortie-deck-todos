# ADR-0001 · 用 LangGraph 编排出击

## 状态

Accepted — 2026-03

## 背景

需要可暂停、可恢复、可分支的出击运行时，并与工作台 HITL 对齐。

## 决策

选用 **LangGraph** `StateGraph` + checkpointer：

- 节点 = 航线阶段（或并行 wave）
- `interrupt()` = 人在环暂停
- `Command` = 恢复 / 改写 / 重路由
- 按任务编译 `custom:{initiative_id}`

## 后果

- 依赖 LangGraph 语义与版本；并行用 wave 节点而非自由 DAG 调度器。
- HITL payload 形状需与 UI 约定同步演进。
- 测试以 wave / interrupt 行为为主（见 `tests/test_parallel_waves.py`）。

## 备选

自研状态机、Temporal、纯 asyncio DAG — 均缺少与现有 HITL / 产物契约的贴合度。
