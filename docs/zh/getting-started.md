# 快速开始

## 环境要求

- Python **3.12+**
- Node.js **18+**（工作台）
- 可选：Postgres（LangGraph checkpointer）

## 安装

```bash
cd Truested-Dev-Teams
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

文档站：

```bash
pip install -e ".[docs]"
mkdocs serve
```

## 运行

```bash
# 终端 1 — API
sortie api
# http://127.0.0.1:8787/api/health

# 终端 2 — 工作台
cd apps/web && npm install && npm run dev
# http://127.0.0.1:5173
```

开发账号：`admin` / `admin123`，`operator` / `operator123`。

## CLI 冒烟

```bash
sortie smoke
```

自动确认航线并演示 HITL 回环。

## 第一个任务（UI）

1. 登录 → **任务** → 新建（简报 + 可选航线提示 / 编制）。
2. 进入 **小队** — 阅读 **航线规划官** 提案。
3. 按需改节点 → **确认航线**（或 `/confirm`）。
4. **开始出击**（或 `/start`）。
5. 门禁用 `/approve` / `/reject` / `/rewrite`。

## 下一步

- [架构总览](architecture/overview.md)
- [航线规划](modules/pipeline.md)
