# 知识库

## 1. 概述

企业级知识库采用腾讯开源 **[WeKnora](https://github.com/Tencent/WeKnora)**。  
Sortie Deck **只做导入与目录管理**；**检索依赖 WeKnora 自身**（hybrid-search），不在本仓库重做向量/RAG。

编码工具（Cursor）通过 Skill 拉取单次任务相关片段并写入 `.cursor/rules`。

| 项 | 值 |
|----|-----|
| 代码 | `knowledge.py`（本地目录镜像）、`weknora.py`、`knowledge_gateway.py`、`knowledge_pack.py` |
| 本地目录 | `data/knowledge.json`（catalog，非全文检索引擎） |
| 后端 | `TDT_KB_BACKEND=local\|weknora` |
| API | `/api/knowledge` · `/status` · `/folders` · `/import` · `/sync` · `/retrieve` |
| CLI | `tdt knowledge {status,sync,import,pack}` |
| Skill | `packages/skills/knowledge-for-cursor` |

## 2. 职责边界

| Sortie Deck | WeKnora |
|-------|---------|
| 导入：Markdown / URL / 文件 | 解析、切分、嵌入、索引 |
| 目录：catalog 列表、folder 镜像、`sync` | 混合检索 hybrid-search |
| 任务 pack → Cursor | FAQ / Wiki / Agent 问答（可选直连 WeKnora） |

## 3. 配置

```bash
TDT_KB_BACKEND=weknora
TDT_WEKNORA_BASE_URL=http://127.0.0.1:8080
TDT_WEKNORA_API_KEY=...
TDT_WEKNORA_KB_ID=<knowledge_base_id>
```

未配置 WeKnora 时回退本地 catalog 关键词（仅开发）。

## 4. 模型

`KnowledgeDoc`：title / summary / tags / category / `folder_path` / `remote_id` / `backend`。  
正文可空（存 WeKnora）；Sortie Deck catalog 只留元数据。

## 5. API

| 方法 | 路径 | 行为 |
|------|------|------|
| GET | `/api/knowledge` | 本地 catalog |
| GET | `/api/knowledge/status` | backend + WeKnora 探活 |
| GET | `/api/knowledge/folders` | 目录树（代理 WeKnora） |
| POST | `/api/knowledge/import` | 导入 file/url/body → WeKnora + catalog |
| POST | `/api/knowledge/sync` | 从 WeKnora 刷新 catalog |
| POST | `/api/knowledge/retrieve` | `{query,limit}` → WeKnora hybrid-search |

## 6. Cursor pack

`load_pack_for_cursor(..., gateway=)` → 检索结果写入：

- `.cursor/rules/sortie-knowledge.mdc`
- `.sortie-deck/knowledge-pack.md`

`cursor_cli` 出击前自动 preload。

## 7. 开发计划

### P0

| 任务 | 验收 |
|------|------|
| WeKnora client + gateway | status / import / sync / retrieve |
| Cursor pack 走 retrieve | `tdt knowledge pack` |
| 文档 | 本文 |

### P1

| 任务 | 验收 |
|------|------|
| Web 导入 / 同步按钮 | 工作台操作 |
| 文件夹移动 UI | 目录管理 |

### P2

| 任务 | 验收 |
|------|------|
| 多 KB / 租户 | 配置多 `kb_id` |
| Claude Code 同构 pack | 完成 |
