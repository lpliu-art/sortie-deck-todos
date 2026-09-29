from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from sortie_deck.toolkit import ToolkitItem

logger = logging.getLogger(__name__)


@dataclass
class McpToolInfo:
    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)


class McpSession:
    """Minimal MCP stdio JSON-RPC client (initialize + tools/list + tools/call)."""

    def __init__(self, item: ToolkitItem) -> None:
        self.item = item
        self._proc: asyncio.subprocess.Process | None = None
        self._next_id = 1
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self.tools: list[McpToolInfo] = []
        self.log: list[str] = []

    async def start(self) -> None:
        if self.item.transport and self.item.transport != "stdio":
            self.log.append(f"skip non-stdio MCP {self.item.name} ({self.item.transport})")
            return
        if not self.item.command:
            self.log.append(f"MCP {self.item.name}: missing command")
            return
        import os

        merged_env = {**os.environ, **(self.item.env or {})}
        self._proc = await asyncio.create_subprocess_exec(
            self.item.command,
            *list(self.item.args or []),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=merged_env,
        )
        assert self._proc.stdin and self._proc.stdout
        self._writer = self._proc.stdin
        self._reader = self._proc.stdout
        await self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "sortie-deck", "version": "0.1.0"},
            },
        )
        await self._notify("notifications/initialized", {})
        listed = await self._request("tools/list", {})
        for raw in (listed or {}).get("tools") or []:
            self.tools.append(
                McpToolInfo(
                    name=str(raw.get("name") or ""),
                    description=str(raw.get("description") or ""),
                    input_schema=raw.get("inputSchema") or {},
                )
            )
        self.log.append(f"MCP {self.item.name}: {len(self.tools)} tools")

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        result = await self._request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        self.log.append(f"call {name}")
        return result

    async def close(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=2)
            except TimeoutError:
                self._proc.kill()
        self._proc = None

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        await self._write({"jsonrpc": "2.0", "method": method, "params": params})

    async def _request(self, method: str, params: dict[str, Any]) -> Any:
        req_id = self._next_id
        self._next_id += 1
        await self._write({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
        while True:
            msg = await self._read()
            if msg is None:
                return None
            if msg.get("id") == req_id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result")

    async def _write(self, payload: dict[str, Any]) -> None:
        if not self._writer:
            return
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        header = f"Content-Length: {len(raw)}\r\n\r\n".encode()
        self._writer.write(header + raw)
        await self._writer.drain()

    async def _read(self) -> dict[str, Any] | None:
        if not self._reader:
            return None
        # Content-Length framed
        headers = b""
        while b"\r\n\r\n" not in headers:
            chunk = await self._reader.readline()
            if not chunk:
                return None
            headers += chunk
        length = 0
        for line in headers.decode().split("\r\n"):
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        body = await self._reader.readexactly(length)
        return json.loads(body.decode("utf-8"))


class McpSessionManager:
    def __init__(self) -> None:
        self.sessions: list[McpSession] = []

    async def open_for_items(self, items: list[ToolkitItem]) -> list[McpSession]:
        opened: list[McpSession] = []
        for item in items:
            if item.kind != "mcp" or not item.enabled:
                continue
            session = McpSession(item)
            try:
                await session.start()
                opened.append(session)
                self.sessions.append(session)
            except Exception as exc:  # noqa: BLE001 — soft-fail per server
                logger.warning("MCP start failed for %s: %s", item.name, exc)
                session.log.append(f"start failed: {exc}")
                opened.append(session)
        return opened

    def tools_manifest(self) -> str:
        lines: list[str] = []
        for s in self.sessions:
            for t in s.tools:
                lines.append(f"- [{s.item.name}] {t.name}: {t.description}")
        return "\n".join(lines)

    def combined_log(self) -> str:
        return "\n".join(line for s in self.sessions for line in s.log)

    async def close_all(self) -> None:
        for s in self.sessions:
            await s.close()
        self.sessions.clear()


def resolve_mcp_items(store: Any, toolkit_ids: list[str]) -> list[ToolkitItem]:
    items: list[ToolkitItem] = []
    if store is None:
        return items
    for tid in toolkit_ids:
        try:
            item = store.get(tid)
        except Exception:
            continue
        if item and item.kind == "mcp" and item.enabled:
            items.append(item)
    return items
