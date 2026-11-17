# 贡献指南

感谢参与 **Sortie Deck**。

## 开发环境

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
cd apps/web && npm install
```

## PR 前检查

```bash
# Python
ruff check src tests
pytest -q

# 工作台
cd apps/web && npx tsc --noEmit

# 文档
mkdocs build --strict
```

## Web 手工冒烟（apps/web）

UI 重构后，请对本地后端走一遍：

1. **登录** — 成功登录；顶栏显示操作员 chip（头像、姓名、角色）。
2. **创建** — 在任务页新建任务并进入 squad 房间。
3. **确认流水线** — 草稿任务中查看阶段；确认（或编辑 → 保存 → 确认）。
4. **启动** — 启动流水线；状态离开 draft，进度轨更新。

## 约定

1. PR 尽量小而聚焦。
2. 控制面行为变更请补测试。
3. 改架构 / 模块时保持中英文档同步。
4. 勿提交密钥、本地 `data/` 转储或个人 `.env`。
5. 遵守仓库根目录行为准则（`CODE_OF_CONDUCT.md`）。

## 文档语言

- README：`README.md`（英）+ `README.zh-CN.md`（中）
- 站点：`docs/en/` + `docs/zh/`，MkDocs 语言切换

## 许可证

贡献即表示同意以 Apache-2.0 授权。
