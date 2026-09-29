from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class ConcurrencyQueue:
    """Simple semaphore-backed queue for batch eng stages."""

    def __init__(self, limit: int = 3) -> None:
        self._limit = limit
        self._sem = asyncio.Semaphore(limit)

    def configure(self, limit: int) -> None:
        """Replace the semaphore when concurrency setting changes."""
        limit = max(1, int(limit))
        if limit == self._limit:
            return
        self._limit = limit
        self._sem = asyncio.Semaphore(limit)

    async def run(self, coro_factory: Callable[[], Awaitable[T]]) -> T:
        async with self._sem:
            return await coro_factory()


ENG_QUEUE = ConcurrencyQueue(limit=3)
