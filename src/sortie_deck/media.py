"""Persist uploaded media (avatars) under data/uploads."""

from __future__ import annotations

import io
import re
from pathlib import Path

from sortie_deck.models import new_id
from sortie_deck.settings import settings

_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def uploads_root() -> Path:
    root = Path(settings.data_dir) / "uploads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def avatars_dir() -> Path:
    d = uploads_root() / "avatars"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_avatar_image(raw: bytes, *, filename: str = "upload.png") -> str:
    """Store image as webp when possible; return public API path ``/api/media/avatars/...``."""
    stem = _SAFE.sub("-", Path(filename).stem)[:40] or "avatar"
    out_name = f"{new_id('av_')}-{stem}.webp"
    dest = avatars_dir() / out_name
    try:
        from PIL import Image

        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGBA")
        # square crop center
        w, h = im.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        im = im.crop((left, top, left + side, top + side))
        im = im.resize((256, 256), Image.Resampling.LANCZOS)
        im.save(dest, "WEBP", quality=88, method=6)
    except Exception:
        # fallback: keep original bytes with original extension
        ext = Path(filename).suffix.lower() or ".bin"
        if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            ext = ".png"
        out_name = f"{new_id('av_')}-{stem}{ext}"
        dest = avatars_dir() / out_name
        dest.write_bytes(raw)
    return f"/api/media/avatars/{dest.name}"
