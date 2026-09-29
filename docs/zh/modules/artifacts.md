# 产物与存储

## 1. 概述

阶段产出的文件存储；任务维护 `ArtifactRef` 索引；API 提供下载。

| 项 | 值 |
|----|-----|
| 代码 | `artifacts.py` |
| 根 | `data/artifacts/<initiative>/<stage>/` |
| API | `GET .../artifacts/{path}` |

## 2. 写入路径

执行器 map → `write_text` → `upstream` → `_sync_artifacts_from_upstream` 追加引用。

## 3. 安全要求

- 防路径穿越
- 下载需登录（后续可加任务成员限制）
- 不执行产物内容

## 4. 技术方案（目标）

- 内容寻址 blob + 引用
- 工程回环 diff API
- S3 兼容后端
- 短时签名 URL

## 5. 开发计划

### P0（2 天）

| 任务 | 验收 |
|------|------|
| 穿越测试 | 拒绝 |
| 下载需鉴权 | 无 token 401 |
| 磁盘布局文档 | 本文 |

### P1（1 周）

| 任务 | 验收 |
|------|------|
| 两版本 diff | API + 简单 UI |
| Ref.meta 存 hash | 有 |

### P2（2 周）

| 任务 | 验收 |
|------|------|
| S3 后端 | 开关 |
| 保留清理任务 | 旧任务可删 |

## 6. 依赖

- Graph 写入、Orchestrator 同步、Web 预览、Contracts 文件名
