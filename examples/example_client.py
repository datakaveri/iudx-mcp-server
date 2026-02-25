"""
IUDX MCP Client — usage examples
=================================

Shows three ways to connect to the IUDX MCP server and call its tools:

  1. Stdio transport  — spawns server.py as a subprocess (local development)
  2. SSE transport    — connects to a running HTTP server (Docker / remote)
  3. Streamable-HTTP  — newer HTTP transport (MCP ≥ 1.3)

Run:
    # Stdio (server started automatically)
    python example_client.py stdio

    # SSE (start server first: MCP_TRANSPORT=sse python server.py)
    python example_client.py sse

    # Streamable-HTTP
    python example_client.py http
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# Resolve server.py relative to this file (one level up)
SERVER_PATH = str(Path(__file__).parent.parent / "server.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print(label: str, data: Any) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print('─' * 60)
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2)[:1200])
    else:
        print(str(data)[:1200])


def _parse_result(result) -> Any:
    """Extract and JSON-parse the first content block of a tool result."""
    if not result.content:
        return {}
    text = result.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# ---------------------------------------------------------------------------
# Demo — runs the same workflow regardless of transport
# ---------------------------------------------------------------------------

async def run_demo(session: ClientSession) -> None:
    await session.initialize()

    # ── List available tools ──────────────────────────────────────────────
    tools_response = await session.list_tools()
    tool_names = [t.name for t in tools_response.tools]
    _print(f"Available tools ({len(tool_names)} total)", tool_names)

    # ── List available resources ──────────────────────────────────────────
    resources_response = await session.list_resources()
    resource_uris = [str(r.uri) for r in resources_response.resources]
    _print(f"Available resources ({len(resource_uris)} total)", resource_uris)

    # ── List available prompts ────────────────────────────────────────────
    prompts_response = await session.list_prompts()
    prompt_names = [p.name for p in prompts_response.prompts]
    _print(f"Available prompts ({len(prompt_names)} total)", prompt_names)

    # ── Tool: count_catalogue_entities ───────────────────────────────────
    result = await session.call_tool("count_catalogue_entities", {})
    _print("count_catalogue_entities", _parse_result(result))

    # ── Tool: get_asset_leaderboard ───────────────────────────────────────
    result = await session.call_tool("get_asset_leaderboard", {})
    data = _parse_result(result)
    top3 = data.get("result", [])[:3]
    _print("get_asset_leaderboard (top 3)", top3)

    # ── Tool: search_catalogue ────────────────────────────────────────────
    result = await session.call_tool("search_catalogue", {
        "search_criteria_json": json.dumps({
            "searchCriteria": [
                {"searchType": "term", "field": "type", "values": ["adex:DataBank"]},
                {"searchType": "term", "field": "accessPolicy", "values": ["OPEN"]},
            ]
        }),
        "filter_fields": ["id", "name", "accessPolicy", "organization"],
        "size": 3,
    })
    _print("search_catalogue (OPEN DataBanks, first 3)", _parse_result(result))

    # ── Tool: get_cat_item ────────────────────────────────────────────────
    # Use the first item ID from the search above
    items = _parse_result(result).get("result", [])
    if items:
        item_id = items[0]["id"]
        result = await session.call_tool("get_cat_item", {"id": item_id})
        _print(f"get_cat_item ({item_id})", _parse_result(result))

    # ── Read a resource ───────────────────────────────────────────────────
    resource_result = await session.read_resource("iudx://leaderboard/assets")
    content_text = resource_result.contents[0].text if resource_result.contents else "{}"
    try:
        resource_data = json.loads(content_text)
        _print("resource: iudx://leaderboard/assets (top 2)", resource_data.get("result", [])[:2])
    except json.JSONDecodeError:
        _print("resource: iudx://leaderboard/assets", content_text[:500])

    # ── Get a prompt ──────────────────────────────────────────────────────
    prompt_result = await session.get_prompt("platform_health_summary", {})
    _print(
        "prompt: platform_health_summary",
        prompt_result.messages[0].content.text if prompt_result.messages else "",
    )

    # ── Tool: RS query (requires Bearer token) ────────────────────────────
    # Uncomment and fill in a real token + resource ID to test RS tools.
    #
    # TOKEN = "eyJ..."           # Bearer JWT from get_token
    # RESOURCE_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    #
    # result = await session.call_tool("rs_get_latest_entity_data", {
    #     "resource_id": RESOURCE_ID,
    #     "token": TOKEN,
    #     "size": 5,
    #     "sort": "observationDateTime:desc",
    # })
    # _print("rs_get_latest_entity_data", _parse_result(result))
    #
    # result = await session.call_tool("rs_get_temporal_entities", {
    #     "resource_id": RESOURCE_ID,
    #     "timerel": "between",
    #     "time_at": "2024-01-01T00:00:00Z",
    #     "end_time_at": "2024-01-07T23:59:59Z",
    #     "token": TOKEN,
    #     "limit": 10,
    #     "format": "simplified",
    # })
    # _print("rs_get_temporal_entities", _parse_result(result))
    #
    # result = await session.call_tool("rs_search_entity_data", {
    #     "resource_id": RESOURCE_ID,
    #     "search_criteria_json": json.dumps({
    #         "searchCriteria": [
    #             {"searchType": "betweenTemporal", "field": "observationDateTime",
    #              "values": ["2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"]}
    #         ],
    #         "filter": ["id", "observationDateTime", "temperature"]
    #     }),
    #     "token": TOKEN,
    #     "size": 5,
    # })
    # _print("rs_search_entity_data", _parse_result(result))

    print("\n✓  Demo complete\n")


# ---------------------------------------------------------------------------
# Transport entry points
# ---------------------------------------------------------------------------

async def connect_stdio() -> None:
    """Connect via stdio — server.py is spawned as a child process."""
    server_params = StdioServerParameters(
        command=sys.executable,   # use the same Python that runs this script
        args=[SERVER_PATH],
        # Pass env vars if needed:
        # env={"IUDX_BASE_URL": "https://v2.prod.controlplane.iudx.io"}
    )
    print("Transport: stdio  (spawning server.py)")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await run_demo(session)


async def connect_sse(url: str = "http://localhost:8000/sse") -> None:
    """Connect via SSE — server must already be running with MCP_TRANSPORT=sse."""
    print(f"Transport: SSE  (url={url})")
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await run_demo(session)


async def connect_streamable_http(url: str = "http://localhost:8000/mcp") -> None:
    """Connect via Streamable HTTP (MCP ≥ 1.3)."""
    try:
        from mcp.client.streamable_http import streamablehttp_client
    except ImportError:
        print("streamable-http transport requires mcp >= 1.3.0")
        return
    print(f"Transport: streamable-http  (url={url})")
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await run_demo(session)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if mode == "stdio":
        asyncio.run(connect_stdio())
    elif mode == "sse":
        url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/sse"
        asyncio.run(connect_sse(url))
    elif mode == "http":
        url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/mcp"
        asyncio.run(connect_streamable_http(url))
    else:
        print(__doc__)
        sys.exit(1)
