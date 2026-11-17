# ADR-0002 · 航线规格先于编译图

## 状态

Accepted — 2026-03

## 背景

固定模板无法覆盖「多端并行 + 分叉自测 + 联调」等动态出击；直接改图代码又难给真人确认。

## 决策

引入 **可编辑的 `pipeline_specs`**（含 `branch` / `parallel_group` / `depends_on`）作为人机确认面：

1. Planner 提案 → 2. 真人确认 → 3. materialize + compile

UI 轨道与运行时共享同一规格源。

## 后果

- 规格是真相源；图是派生物。
- 需维护 planner（启发式 / LLM）与校验。
- 并行语义集中在 `parallel.py`。

## 备选

仅用静态 YAML 模板、或纯自然语言每次现编图 — 分别缺动态性或缺可审计结构。
