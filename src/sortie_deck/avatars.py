"""Role avatar presets for squad loadout + pipeline rail."""

from __future__ import annotations

from typing import Any

# Built-in comic/pixel portraits live under apps/web/public/avatars/*.webp
AVATAR_PRESETS: list[dict[str, Any]] = [
    {
        "id": "preset:product",
        "role": "product",
        "label": "Product",
        "label_zh": "产品官",
        "hue": 28,
        "src": "/avatars/product.webp",
    },
    {
        "id": "preset:design",
        "role": "design",
        "label": "Design",
        "label_zh": "设计",
        "hue": 265,
        "src": "/avatars/design.webp",
    },
    {
        "id": "preset:eng",
        "role": "eng",
        "label": "Engineer",
        "label_zh": "工程",
        "hue": 152,
        "src": "/avatars/eng.webp",
    },
    {
        "id": "preset:eng_ios",
        "role": "eng_ios",
        "label": "iOS",
        "label_zh": "iOS",
        "hue": 200,
        "src": "/avatars/eng_ios.webp",
    },
    {
        "id": "preset:eng_android",
        "role": "eng_android",
        "label": "Android",
        "label_zh": "Android",
        "hue": 130,
        "src": "/avatars/eng_android.webp",
    },
    {
        "id": "preset:eng_web",
        "role": "eng_web",
        "label": "Web",
        "label_zh": "Web",
        "hue": 190,
        "src": "/avatars/eng_web.webp",
    },
    {
        "id": "preset:eng_backend",
        "role": "eng_backend",
        "label": "Backend",
        "label_zh": "后端",
        "hue": 210,
        "src": "/avatars/eng_backend.webp",
    },
    {
        "id": "preset:eng_agent",
        "role": "eng_agent",
        "label": "Agent",
        "label_zh": "Agent",
        "hue": 300,
        "src": "/avatars/eng_agent.webp",
    },
    {
        "id": "preset:qa",
        "role": "qa",
        "label": "QA",
        "label_zh": "测试",
        "hue": 45,
        "src": "/avatars/qa.webp",
    },
    {
        "id": "preset:deploy",
        "role": "deploy",
        "label": "Deploy",
        "label_zh": "发布",
        "hue": 170,
        "src": "/avatars/deploy.webp",
    },
    {
        "id": "preset:ops",
        "role": "ops",
        "label": "Ops",
        "label_zh": "指挥",
        "hue": 0,
        "src": "/avatars/eng.webp",
    },
]


def default_avatar_for_role(role: str) -> str:
    rid = (role or "").strip().lower()
    for p in AVATAR_PRESETS:
        if p["role"] == rid:
            return str(p["id"])
    return f"preset:{rid or 'ops'}"


def preset_src(avatar_or_role: str) -> str | None:
    """Resolve preset:<role> or bare role → public webp path."""
    key = (avatar_or_role or "").strip()
    if key.startswith("preset:"):
        key = key[7:]
    for p in AVATAR_PRESETS:
        if p["role"] == key or p["id"] == f"preset:{key}":
            return str(p.get("src") or f"/avatars/{p['role']}.webp")
    return None


def list_avatar_presets() -> list[dict[str, Any]]:
    return list(AVATAR_PRESETS)
