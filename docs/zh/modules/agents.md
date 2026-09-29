# 角色工坊

## 1. 概述

发布专业角色（人设、编制位、可见性、默认 `toolkit_ids`）供任务点名。

| 项 | 值 |
|----|-----|
| 代码 | `agents.py` |
| 存储 | `data/agents.json` |
| API | `/api/agents` CRUD |

## 2. 模型

`PublishedAgent`：slot、persona、toolkit_ids、visibility、version…  
创建任务时 `resolve_slot_map`。

## 3. 种子角色（开发）

新建 `data/agents.json` 时内置公开专家：

| Slug | 编制位 | 说明 |
|------|--------|------|
| `prd-scout` | product | 前场 PRD 侦察 |
| `design-navigator` | design | 交互 / 视觉规格 |
| `platform-eng-raider` | eng | 通用工程突击 |
| `ios-raider` | eng_ios | iOS |
| `android-raider` | eng_android | Android |
| `web-raider` | eng_web | Web 前端 |
| `backend-raider` | eng_backend | 后端 / API |
| `agent-raider` | eng_agent | Agent / MCP / 评测 |
| `qa-gatekeeper` | qa | 门禁 QA |

编制位：`product` · `design` · `eng` · `eng_ios` · `eng_android` · `eng_web` · `eng_backend` · `eng_agent` · `qa` · `deploy`。

## 4. 流程

专家发布（可带默认工具）→ 建任务点名 → 运行时用已发布 persona。

## 5. 技术方案（目标）

- semver + 任务钉扎
- 人设评测架
- 组织目录同步

## 6. 开发计划

### P0（1–2 天）

| 任务 | 验收 |
|------|------|
| API/UI 展示 toolkit_ids | 可见 |
| 仅作者可改测试 | pytest |
| 种子角色说明 | README |

### P1（1 周）

| 任务 | 验收 |
|------|------|
| patch 升 version；创建钉扎 | meta 有 pin |
| 克隆角色 | 新 slug |

### P2（2 周）

| 任务 | 验收 |
|------|------|
| 评测 CLI | 出分报告 |
| 远程组织目录 | pull |

## 7. 依赖

- Toolkit、Orchestrator 编制、Web 工坊
