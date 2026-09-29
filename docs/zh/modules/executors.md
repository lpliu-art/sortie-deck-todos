# 执行器与插件

## 1. 概述

将 `StageContext` 变成 `StageResult` 产物的阶段运行器；编码/发布提供者可替换。

| 项 | 值 |
|----|-----|
| 注册表 | `registry.py`、`plugins/factory.py` |
| 队列 | `ENG_QUEUE` |
| 实现 | `mock.py`、`coding.py`、`deploy.py` |

## 2. 协议

```python
async def run(self, ctx: StageContext) -> StageResult: ...
```

上下文含 brief、persona（含工具 brief）、上游产物文本、workspace、permissions。

## 3. 内置

| 名称 | 用途 | 说明 |
|------|------|------|
| mock_* | 演示 | 确定性产物 |
| mock_qa_cases / selftest / integrate / handoff | 标准轨 | |
| claude_code / cursor_cli | 工程实现 | worktree |
| deploy_shell | 发布 | `TDT_DEPLOY_CMD` |
| llm_product | 可选 PRD | 需 LLM Key |

解析：模板 executor 字段，否则 `graph._executor_name` 按 coding/deploy 配置。

## 4. 技术方案（目标）

- `probe()` 健康检查
- 日志流式进频道
- shell 沙箱档案
- `sortie_deck.executors` 社区入口

## 5. 开发计划

### P0（2–3 天）

| 任务 | 验收 |
|------|------|
| README：Claude/Cursor 环境 | 可照做 |
| 注册列表测试 | pytest |
| CLI 缺失时软失败 | 明确 message |

### P1（1–2 周）

| 任务 | 验收 |
|------|------|
| 日志流挂钩 | 小队可见 |
| `/api/executors` 带 probe | status 字段 |
| 编码执行器调 MCP | 开关 |

### P2（2 周）

| 任务 | 验收 |
|------|------|
| entry points 发现插件 | 可外载（`sortie_deck.executors`；示例 `packages/examples/demo_executor`） |
| `/api/executors` probe | 已返回 `probes` |
| 时限/资源限制 | 待续 |

## 6. 测试计划

- mock 满足契约；队列并发；缺二进制不崩

## 7. 依赖

- Graph、Toolkit brief、Artifacts、Settings
