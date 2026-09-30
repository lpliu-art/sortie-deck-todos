# ADR-0003 · 决策器可选挂载（TypeSafe Jev）

## 状态

Proposed — 见 [TODO.md](../../../../TODO.md)

## 背景

人在环需要「建议 / 结构化决策」，但不希望把出击暂停语义绑死在某一厂商。

## 决策（方向）

- **Jev System One（typesafe.ai）** 作为可选决策挂载：输出建议动作与理由。
- **LangGraph `interrupt()` 仍是唯一暂停真相**；Jev 不替代门禁。
- 失败降级为纯人工 HITL。

## 后果

- 集成边界清晰：建议 ≠ 自动批准。
- 文档与 TOPIC 可强调「HITL + optional decisioner」。
- 实现前保持 Proposed，避免空承诺。

## 备选

内置规则引擎、或无决策器仅 UI 按钮 — 均可作默认路径。
