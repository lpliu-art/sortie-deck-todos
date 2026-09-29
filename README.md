# Sortie Deck — 后续 TODO

本仓库集中存放 [Sortie Deck](https://github.com/lpliu-art) 控制面的下一阶段规划，与实现仓分离，便于评审与排期。

主文档：[TODO.md](./TODO.md)

## 与实现的关系

- **运行时**：LangGraph 编排阶段 / 并行波次 / HITL；房间频道、产物、执行器在 Sortie Deck 主仓。
- **本仓**：只记录尚未落地的能力切片、约束、设想中的决策层（TypeSafe Jev）。

## 主题索引

| # | 主题 | 一句话 |
|---|------|--------|
| 1 | [真人频道与角色绑定](./TODO.md#1-真人频道与角色绑定) | 真人进频道、一角一人、确认/权限档、钉钉飞书 |
| 2 | [知识库](./TODO.md#2-知识库目录--worktree--标签) | 目录/worktree + 全局/业务/任务标签 |
| 3 | [记忆管理](./TODO.md#3-记忆管理分层--双存储) | 分层作用域 + 文件式 / 向量 |
| 4 | [工具与技能拆分](./TODO.md#4-工具与技能拆分) | Toolkit 与 Skill 解耦 |
| 5 | [系统自迭代](./TODO.md#5-系统自迭代) | 用任务与沟通沉淀驱动控制面进化 |
| 6 | [Jev 决策指挥层](./TODO.md#6-jev-决策指挥层设想) | 决策交给 [TypeSafe Jev](https://console.typesafe.ai/) |

## 建议阅读顺序

先读 TODO 文末的优先级与依赖图，再按 P0 → P1 → P2 拆 issue。
