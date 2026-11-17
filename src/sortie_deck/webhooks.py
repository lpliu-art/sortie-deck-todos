from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def notify_webhook(url: str | None, event: str, payload: dict[str, Any], timeout: float = 5.0) -> None:
    if not url:
        return
    body = {"event": event, **payload}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            await client.post(url, json=body)
    except Exception as exc:  # noqa: BLE001 — best-effort hook
        logger.warning("webhook failed: %s", exc)
