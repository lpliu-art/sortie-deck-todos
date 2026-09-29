from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from sortie_deck.models import new_id, utc_now


class KnowledgeDoc(BaseModel):
    id: str = Field(default_factory=lambda: new_id("kb_"))
    title: str
    summary: str = ""
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    category: Literal["playbook", "runbook", "lore", "reference"] = "playbook"
    author_id: str = ""
    author_name: str = ""
    # Enterprise KB mirror (WeKnora) — Sortie Deck catalogs; retrieval is remote
    backend: Literal["local", "weknora"] = "local"
    remote_id: str | None = None
    remote_kb_id: str | None = None
    folder_path: str = ""
    parse_status: str = ""
    created_at: str = Field(default_factory=lambda: utc_now().isoformat())
    updated_at: str = Field(default_factory=lambda: utc_now().isoformat())


class CreateKnowledgeRequest(BaseModel):
    title: str
    summary: str = ""
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    category: Literal["playbook", "runbook", "lore", "reference"] = "playbook"


class UpdateKnowledgeRequest(BaseModel):
    title: str | None = None
    summary: str | None = None
    body: str | None = None
    tags: list[str] | None = None
    category: Literal["playbook", "runbook", "lore", "reference"] | None = None


_SEED: list[dict] = [
    {
        "title": "Fireteam 作战手册",
        "summary": "前场小队如何对齐、出征、门禁与回写知识库",
        "category": "playbook",
        "tags": ["playbook", "fireteam"],
        "body": (
            "# Fireteam Playbook\n\n"
            "Sortie Deck 把每次交付当成一次 **前线任务（Mission）**：\n"
            "- 真人 = 前场指挥官（门禁 / Clearance）\n"
            "- Agent 角色 = 小队专精位（Product / Eng / QA / Deploy）\n"
            "- 讨论先于开战：小队对齐后再 `/start`\n"
            "- 产物与决策回写 Codex，避免再当传话筒\n\n"
            "相关文档：[Mission Clearance 门禁规则](mission-clearance) · "
            "[Codex 写入约定](codex-conventions)\n"
        ),
    },
    {
        "title": "Mission Clearance 门禁规则",
        "summary": "HITL 批准/拒绝/重写的前线纪律",
        "category": "runbook",
        "tags": ["hitl", "clearance"],
        "body": (
            "# Clearance\n\n"
            "- `approve`：放行下一阶段\n"
            "- `reject` / `rewrite`：带着指令回环\n"
            "- `stop`：任务中止\n"
            "指挥官只守门，专精位负责推进。\n\n"
            "前置阅读：[Fireteam 作战手册](fireteam-playbook)\n"
        ),
    },
    {
        "title": "Codex 写入约定",
        "summary": "任务结束后沉淀可复用情报",
        "category": "reference",
        "tags": ["codex", "knowledge"],
        "body": (
            "# Codex\n\n"
            "每次 Mission 收尾，至少沉淀：背景、决策、坑点、可复用片段。\n"
            "标签建议：`customer` / `stack` / `failure` / `pattern`。\n\n"
            "流程背景：[Fireteam 作战手册](fireteam-playbook) · "
            "门禁细节：[Mission Clearance 门禁规则](mission-clearance)\n"
        ),
    },
    {
        "title": "门户预览健康检查约定",
        "summary": "office portal preview 健康检查接口约定",
        "category": "reference",
        "tags": ["api", "openapi", "portal", "health"],
        "body": (
            "# Preview health API\n\n"
            "- `GET /api/health` 返回 `{ status, product }`\n"
            "- 预发环境须可匿名探活；勿返回密钥\n"
            "- 工程实现优先复用现有 FastAPI health，避免平行端点\n"
        ),
    },
    {
        "title": "办公门户产品边界",
        "summary": "office portal 产品范围与非目标",
        "category": "reference",
        "tags": ["product", "portal", "spec"],
        "body": (
            "# Office portal product\n\n"
            "## 范围内\n"
            "- 预览环境可达性与健康展示\n"
            "- 与 Sortie Deck 任务产物联动\n\n"
            "## 非目标\n"
            "- 完整 IAM / 多租户控制台\n"
        ),
    },
    {
        "title": "预发发布技术方案摘要",
        "summary": "preview deploy 技术选型摘要",
        "category": "reference",
        "tags": ["design", "architecture", "deploy", "preview"],
        "body": (
            "# Preview deploy design\n\n"
            "- 产物落盘 `data/artifacts/<mission>/`\n"
            "- Deploy 门禁人工确认后再切流量\n"
            "- 编码阶段使用 Cursor 时加载知识包 `.cursor/rules/sortie-knowledge.mdc`\n"
        ),
    },
]


class KnowledgeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.path.exists():
            docs = []
            for seed in _SEED:
                docs.append(
                    KnowledgeDoc(
                        title=seed["title"],
                        summary=seed["summary"],
                        body=seed["body"],
                        tags=seed["tags"],
                        category=seed["category"],
                        author_name="Sortie",
                    )
                )
            self._write(docs)

    def _read(self) -> list[KnowledgeDoc]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [KnowledgeDoc.model_validate(x) for x in raw]

    def _write(self, docs: list[KnowledgeDoc]) -> None:
        self.path.write_text(
            json.dumps([d.model_dump(mode="json") for d in docs], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list(self, q: str | None = None) -> list[KnowledgeDoc]:
        with self._lock:
            docs = self._read()
        if not q:
            return sorted(docs, key=lambda d: d.updated_at, reverse=True)
        needle = q.lower()
        filtered = [
            d
            for d in docs
            if needle in d.title.lower()
            or needle in d.summary.lower()
            or needle in d.body.lower()
            or any(needle in t.lower() for t in d.tags)
        ]
        return sorted(filtered, key=lambda d: d.updated_at, reverse=True)

    def get(self, doc_id: str) -> KnowledgeDoc:
        for d in self.list():
            if d.id == doc_id:
                return d
        raise KeyError(doc_id)

    def create(self, req: CreateKnowledgeRequest, *, author_id: str, author_name: str) -> KnowledgeDoc:
        doc = KnowledgeDoc(
            title=req.title.strip(),
            summary=req.summary.strip(),
            body=req.body,
            tags=[t.strip() for t in req.tags if t.strip()],
            category=req.category,
            author_id=author_id,
            author_name=author_name,
        )
        with self._lock:
            docs = self._read()
            docs.append(doc)
            self._write(docs)
        return doc

    def update(self, doc_id: str, req: UpdateKnowledgeRequest) -> KnowledgeDoc:
        with self._lock:
            docs = self._read()
            for i, d in enumerate(docs):
                if d.id != doc_id:
                    continue
                data = d.model_dump()
                patch = req.model_dump(exclude_unset=True)
                if "title" in patch and patch["title"] is not None:
                    patch["title"] = patch["title"].strip()
                if "summary" in patch and patch["summary"] is not None:
                    patch["summary"] = patch["summary"].strip()
                if "tags" in patch and patch["tags"] is not None:
                    patch["tags"] = [t.strip() for t in patch["tags"] if t.strip()]
                data.update(patch)
                data["updated_at"] = utc_now().isoformat()
                docs[i] = KnowledgeDoc.model_validate(data)
                self._write(docs)
                return docs[i]
        raise KeyError(doc_id)

    def delete(self, doc_id: str) -> None:
        with self._lock:
            docs = self._read()
            next_docs = [d for d in docs if d.id != doc_id]
            if len(next_docs) == len(docs):
                raise KeyError(doc_id)
            self._write(next_docs)
