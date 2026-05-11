"""Lovable MCP client wrapper.

Talks to https://mcp.lovable.dev using the Python MCP SDK.
Phase 2 — these functions will be wired into the CLI once the API key
is set up in the runtime environment.
"""
from __future__ import annotations
import asyncio
import base64
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Optional

LOVABLE_MCP_URL = "https://mcp.lovable.dev"


def _api_key() -> str:
    key = os.environ.get("LOVABLE_API_KEY")
    if not key:
        raise RuntimeError(
            "LOVABLE_API_KEY not set. Get one from Lovable -> Settings -> "
            "API keys (starts with 'lov_') and put it in .env."
        )
    return key


@asynccontextmanager
async def _session() -> AsyncIterator[Any]:
    """Open an MCP session against mcp.lovable.dev."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    headers = {"Lovable-API-Key": _api_key()}
    async with streamablehttp_client(LOVABLE_MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def list_tools_async() -> list[str]:
    async with _session() as s:
        result = await s.list_tools()
        return [t.name for t in result.tools]


def list_tools() -> list[str]:
    return asyncio.run(list_tools_async())


async def create_project_async(*, name: str, initial_message: str,
                               workspace_id: Optional[str] = None) -> dict:
    """Create a Lovable project from a prompt. Returns the project dict
    including id, editor_url, preview_url."""
    args: dict[str, Any] = {"name": name, "initial_message": initial_message}
    if workspace_id:
        args["workspace_id"] = workspace_id
    async with _session() as s:
        result = await s.call_tool("create_project", args)
        return _unwrap(result)


def create_project(name: str, initial_message: str,
                  workspace_id: Optional[str] = None) -> dict:
    return asyncio.run(create_project_async(
        name=name, initial_message=initial_message, workspace_id=workspace_id))


async def get_project_async(project_id: str) -> dict:
    """Get project details including a screenshot (base64 PNG)."""
    async with _session() as s:
        result = await s.call_tool("get_project", {"project_id": project_id})
        return _unwrap(result)


def get_project(project_id: str) -> dict:
    return asyncio.run(get_project_async(project_id))


async def deploy_project_async(project_id: str) -> dict:
    async with _session() as s:
        result = await s.call_tool("deploy_project", {"project_id": project_id})
        return _unwrap(result)


def deploy_project(project_id: str) -> dict:
    return asyncio.run(deploy_project_async(project_id))


async def send_message_async(project_id: str, message: str,
                             wait: bool = True) -> dict:
    async with _session() as s:
        result = await s.call_tool("send_message", {
            "project_id": project_id, "message": message, "wait": wait,
        })
        return _unwrap(result)


def send_message(project_id: str, message: str, wait: bool = True) -> dict:
    return asyncio.run(send_message_async(project_id, message, wait))


def save_screenshot(b64_or_url: str, dest: Path) -> Path:
    """Persist a screenshot returned by get_project to disk."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if b64_or_url.startswith(("http://", "https://")):
        import httpx
        dest.write_bytes(httpx.get(b64_or_url, timeout=30).content)
    else:
        payload = b64_or_url.split(",", 1)[-1]
        dest.write_bytes(base64.b64decode(payload))
    return dest


def _unwrap(result: Any) -> dict:
    """MCP responses may be wrapped in a content list. Normalise to dict."""
    if hasattr(result, "structuredContent") and result.structuredContent:
        return dict(result.structuredContent)
    if hasattr(result, "content"):
        for block in result.content:
            if getattr(block, "type", "") == "text":
                import json
                try:
                    return json.loads(block.text)
                except Exception:
                    return {"text": block.text}
    return dict(result) if isinstance(result, dict) else {"raw": str(result)}
