import json
import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("IUDX_BASE_URL", "https://v2.dev.controlplane.iudx.io")
RS_BASE_URL = os.getenv("RS_BASE_URL", "https://v2.dev.rs.iudx.io")
RSP_BASE_URL = os.getenv("RSP_BASE_URL", "https://v2.dev.rs.iudx.io/rsp")
FILES_BASE_URL = os.getenv("FILES_BASE_URL", "https://v2.dev.file-s3.iudx.io/v1")
ES_INDEX_PREFIX = os.getenv("ES_INDEX_PREFIX", "")

# Persistent per-service HTTP clients — created once at import time,
# reused across all tool calls for connection pooling (eliminates TCP/TLS overhead).
_clients: dict[str, httpx.AsyncClient] = {
    "cat":   httpx.AsyncClient(timeout=30),
    "rs":    httpx.AsyncClient(timeout=60),
    "rsp":   httpx.AsyncClient(timeout=60),
    "files": httpx.AsyncClient(timeout=30),
}
logger.info("HTTP clients initialized (persistent connection pooling enabled)")

mcp = FastMCP("IUDX MCP Server")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _rs_headers(token: str, did: str = "") -> dict[str, str]:
    h: dict[str, str] = {}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if did:
        h["did"] = did
    return h


def _parse(raw: str, name: str = "payload") -> dict:
    """json.loads with a readable error."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in '{name}': {exc}") from exc


def _fmt_item(item: dict) -> str:
    tags = item.get("tags") or []
    return "\n".join([
        f"ID:           {item.get('id', 'N/A')}",
        f"Name:         {item.get('name') or item.get('label', 'N/A')}",
        f"Description:  {item.get('description') or item.get('shortDescription', 'N/A')}",
        f"Type:         {', '.join(item.get('type', []))}",
        f"Organization: {item.get('organization', 'N/A')}",
        f"AccessPolicy: {item.get('accessPolicy', 'N/A')}",
        f"Tags:         {', '.join(tags) if tags else 'N/A'}",
        f"DataReadiness:{item.get('dataReadiness', 'N/A')}",
        f"Created:      {item.get('itemCreatedAt', 'N/A')}",
    ])


# ---------------------------------------------------------------------------
# Control Plane HTTP helpers
# ---------------------------------------------------------------------------

async def _get(
    path: str, *, token: str = "", params: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("GET %s params=%s", url, params)
    r = await _clients["cat"].get(url, params=params, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _post(
    path: str,
    *,
    token: str = "",
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("POST %s params=%s", url, params)
    r = await _clients["cat"].post(url, params=params, json=body, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _put(
    path: str, *, token: str = "", body: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("PUT %s", url)
    r = await _clients["cat"].put(url, json=body, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _patch(
    path: str,
    *,
    token: str = "",
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("PATCH %s params=%s", url, params)
    r = await _clients["cat"].patch(url, params=params, json=body, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _delete(
    path: str, *, token: str = "", params: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("DELETE %s params=%s", url, params)
    r = await _clients["cat"].delete(url, params=params, headers=_headers(token))
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Resource Server HTTP helpers
# ---------------------------------------------------------------------------

async def _rs_get(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
) -> dict:
    url = f"{RS_BASE_URL}{path}"
    logger.info("RS GET %s params=%s", url, params)
    r = await _clients["rs"].get(url, params=params, headers=_rs_headers(token, did))
    r.raise_for_status()
    return r.json()


async def _rs_post(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
    body: Any = None,
) -> dict:
    url = f"{RS_BASE_URL}{path}"
    logger.info("RS POST %s params=%s", url, params)
    r = await _clients["rs"].post(url, params=params, json=body, headers=_rs_headers(token, did))
    r.raise_for_status()
    return r.json()


async def _rs_get_text(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
) -> str:
    """GET that returns raw text (used for CSV download endpoints)."""
    url = f"{RS_BASE_URL}{path}"
    logger.info("RS GET (text) %s params=%s", url, params)
    r = await _clients["rs"].get(url, params=params, headers=_rs_headers(token, did), timeout=120)
    r.raise_for_status()
    return r.text


async def _rs_post_text(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
    body: Any = None,
) -> str:
    """POST that returns raw text (used for CSV download endpoints)."""
    url = f"{RS_BASE_URL}{path}"
    logger.info("RS POST (text) %s params=%s", url, params)
    r = await _clients["rs"].post(url, params=params, json=body, headers=_rs_headers(token, did), timeout=120)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Resource Server Proxy HTTP helpers
# ---------------------------------------------------------------------------

async def _rsp_get(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
) -> dict:
    url = f"{RSP_BASE_URL}{path}"
    logger.info("RSP GET %s params=%s", url, params)
    r = await _clients["rsp"].get(url, params=params, headers=_rs_headers(token, did))
    r.raise_for_status()
    return r.json()


async def _rsp_post(
    path: str,
    *,
    token: str = "",
    did: str = "",
    params: dict[str, Any] | None = None,
    body: Any = None,
) -> dict:
    url = f"{RSP_BASE_URL}{path}"
    logger.info("RSP POST %s params=%s", url, params)
    r = await _clients["rsp"].post(url, params=params, json=body, headers=_rs_headers(token, did))
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Files Connect HTTP helpers
# ---------------------------------------------------------------------------

async def _files_get(
    path: str, *, token: str = "", params: dict[str, Any] | None = None
) -> dict:
    url = f"{FILES_BASE_URL}{path}"
    logger.info("FILES GET %s params=%s", url, params)
    r = await _clients["files"].get(url, params=params, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _files_post(
    path: str,
    *,
    token: str = "",
    body: dict[str, Any] | None = None,
) -> dict:
    url = f"{FILES_BASE_URL}{path}"
    logger.info("FILES POST %s", url)
    r = await _clients["files"].post(url, json=body, headers=_headers(token))
    r.raise_for_status()
    return r.json()


async def _files_put(
    path: str,
    *,
    token: str = "",
    body: dict[str, Any] | None = None,
) -> dict:
    url = f"{FILES_BASE_URL}{path}"
    logger.info("FILES PUT %s", url)
    r = await _clients["files"].put(url, json=body, headers=_headers(token))
    r.raise_for_status()
    return r.json()
