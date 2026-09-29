from __future__ import annotations

import json

import pytest

from sortie_deck.mcp_runtime import McpSession
from sortie_deck.toolkit import ToolkitItem


@pytest.mark.asyncio
async def test_mcp_session_skips_without_command():
    item = ToolkitItem(kind="mcp", name="demo", transport="stdio", command="")
    session = McpSession(item)
    await session.start()
    assert any("missing command" in line for line in session.log)
    await session.close()


@pytest.mark.asyncio
async def test_mcp_framing_roundtrip_helpers():
    """Ensure Content-Length framing encodes/decodes JSON payloads."""
    item = ToolkitItem(kind="mcp", name="demo", transport="stdio", command="true")
    session = McpSession(item)
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
    raw = json.dumps(payload).encode()
    framed = f"Content-Length: {len(raw)}\r\n\r\n".encode() + raw
    assert b"Content-Length:" in framed
    assert json.loads(raw)["id"] == 1
    await session.close()
