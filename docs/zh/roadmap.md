# 路线图

Sortie Deck 作为开源控制面的跨模块里程碑。

各模块细化计划（任务、验收、估时）见 [模块](modules/auth.md)。

## 建议交付顺序

1. **入口**：[认证](modules/auth.md) → [Web](modules/web.md) → [CLI](modules/cli.md)
2. **核心环**：[编排](modules/orchestrator.md) → [航线](modules/pipeline.md) → [图与门禁](modules/graph.md) → [小队](modules/rooms.md)
3. **平台**：[执行器](modules/executors.md) → [工具箱](modules/toolkit.md) → [角色](modules/agents.md) → [知识](modules/knowledge.md) / [记忆](modules/memory.md) → [产物](modules/artifacts.md)

## P0 — OSS 硬化

- CI：`ruff`、pytest、工作台 `tsc`、`mkdocs build`
- 安全评审：token、产物路径穿越、工具箱导入
- `.env.example` 与执行器配置指南
- Issue / PR 模板

## P1 — 存储与规划

- [x] 现有 store 接口下的 SQL 仓储（`TDT_STORAGE=sqlite`，任务级）
- [x] 可选 LLM 航线规划官（`TDT_PIPELINE_LLM`；人手确认仍强制；失败回落启发式）
- [x] 编码执行器接入 MCP 运行时（`TDT_MCP_RUNTIME`，stdio list/tools → prompt）
- [x] 小队 @ 讨论 LLM（`TDT_ROOM_LLM`；失败回落模板）

## P2 — 生产运维

- [x] 多 worker 运行队列与锁（`TDT_RUN_BACKEND=sqlite` + lease）
- [x] S3 兼容产物（`TDT_ARTIFACT_BACKEND=s3`，可选 `.[s3]`）
- [x] 工具 / 航线组织策略（`TDT_ORG_POLICY_PATH` + `packages/policies/default.json`）
- [x] 外部聊天桥（`/api/bridges/slack` · `/api/bridges/feishu`）
- [x] 社区执行器打包（entry point 组 `sortie_deck.executors` + `packages/examples/demo_executor`）

## 近期非目标

- 用自研引擎替换 LangGraph
- 仅闭源 SaaS 核心
