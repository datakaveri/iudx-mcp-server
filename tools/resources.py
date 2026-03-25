import json
import httpx
from ._app import mcp, _get, _post, _rsp_get, _fmt_item


# ===========================================================================
# RESOURCES — public, cacheable, URI-addressable
# ===========================================================================

@mcp.resource("iudx://catalogue/datasets")
async def resource_datasets() -> str:
    """First 100 publicly discoverable IUDX DataBank items."""
    body = {
        "searchCriteria": [{"searchType": "term", "field": "type",
                            "values": ["adex:DataBank"]}],
        "filter": ["id", "name", "label", "accessPolicy", "organization", "tags"],
    }
    data = await _post("/iudx/v2/cat/search", params={"page": 1, "size": 100}, body=body)
    results = data.get("result", [])
    if not results:
        return "No datasets found."
    total = data.get("totalHits", len(results))
    lines = [
        f"- {r.get('id')} | {r.get('name') or r.get('label', 'N/A')} "
        f"| {r.get('organization', 'N/A')} | {r.get('accessPolicy', 'N/A')}"
        for r in results
    ]
    return f"IUDX DataBank Datasets ({len(results)} of {total}):\n" + "\n".join(lines)


@mcp.resource("iudx://catalogue/datasets/{id}")
async def resource_dataset(id: str) -> str:
    """Full metadata for a specific IUDX catalogue item by UUID."""
    try:
        data = await _get("/iudx/v2/cat/item", params={"id": id})
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return f"Item '{id}' not found."
        raise
    results = data.get("result", [])
    return _fmt_item(results[0]) if results else f"No data for item '{id}'."


@mcp.resource("iudx://catalogue/ai_models")
async def resource_ai_models() -> str:
    """First 100 publicly discoverable IUDX AI Model items."""
    body = {
        "searchCriteria": [{"searchType": "term", "field": "type",
                            "values": ["adex:AiModel"]}],
        "filter": ["id", "name", "label", "accessPolicy", "organization", "tags"],
    }
    data = await _post("/iudx/v2/cat/search", params={"page": 1, "size": 100}, body=body)
    results = data.get("result", [])
    if not results:
        return "No AI models found."
    total = data.get("totalHits", len(results))
    lines = [
        f"- {r.get('id')} | {r.get('name') or r.get('label', 'N/A')} "
        f"| {r.get('organization', 'N/A')} | {r.get('accessPolicy', 'N/A')}"
        for r in results
    ]
    return f"IUDX AI Models ({len(results)} of {total}):\n" + "\n".join(lines)


@mcp.resource("iudx://catalogue/apps")
async def resource_apps() -> str:
    """First 100 publicly discoverable IUDX Application items."""
    body = {
        "searchCriteria": [{"searchType": "term", "field": "type",
                            "values": ["adex:Apps"]}],
        "filter": ["id", "name", "label", "accessPolicy", "organization", "tags"],
    }
    data = await _post("/iudx/v2/cat/search", params={"page": 1, "size": 100}, body=body)
    results = data.get("result", [])
    if not results:
        return "No apps found."
    total = data.get("totalHits", len(results))
    lines = [
        f"- {r.get('id')} | {r.get('name') or r.get('label', 'N/A')} "
        f"| {r.get('organization', 'N/A')} | {r.get('accessPolicy', 'N/A')}"
        for r in results
    ]
    return f"IUDX Apps ({len(results)} of {total}):\n" + "\n".join(lines)


@mcp.resource("iudx://dashboard/usage_summary")
async def resource_usage_summary() -> str:
    """Platform-wide IUDX usage metrics."""
    data = await _get("/iudx/v2/dashboard/usage-summary")
    result = data.get("result", data)
    if isinstance(result, list) and result:
        result = result[0]
    if isinstance(result, dict):
        lines = [f"{k}: {v}" for k, v in result.items()]
        return "IUDX Usage Summary:\n" + "\n".join(lines)
    return f"IUDX Usage Summary:\n{result}"


@mcp.resource("iudx://leaderboard/assets")
async def resource_leaderboard_assets() -> str:
    """IUDX asset leaderboard."""
    data = await _get("/iudx/v2/leaderboard/asset")
    results = data.get("result", [])
    if not results:
        return "No leaderboard data."
    lines = [f"{i+1}. {r}" for i, r in enumerate(results)]
    return "IUDX Asset Leaderboard:\n" + "\n".join(lines)


@mcp.resource("iudx://leaderboard/providers")
async def resource_leaderboard_providers() -> str:
    """IUDX provider leaderboard."""
    data = await _get("/iudx/v2/leaderboard/provider")
    results = data.get("result", [])
    if not results:
        return "No leaderboard data."
    lines = [f"{i+1}. {r}" for i, r in enumerate(results)]
    return "IUDX Provider Leaderboard:\n" + "\n".join(lines)


@mcp.resource("iudx://leaderboard/organizations")
async def resource_leaderboard_orgs() -> str:
    """IUDX organisation leaderboard."""
    data = await _get("/iudx/v2/leaderboard/organization")
    results = data.get("result", [])
    if not results:
        return "No leaderboard data."
    lines = [f"{i+1}. {r}" for i, r in enumerate(results)]
    return "IUDX Organisation Leaderboard:\n" + "\n".join(lines)


@mcp.resource("iudx://rsp/entities/{id}")
async def resource_rsp_entities(id: str) -> str:
    """Latest spatial snapshot for an IUDX resource via the Resource Server Proxy (RSP v2).

    Fetches the most recent entity data for the given resource ID through the RSP,
    returning a JSON summary. Requires a public/OPEN resource; SECURE resources
    need a Bearer token (use rsp_get_entities_v2 directly for authenticated access).
    """
    try:
        data = await _rsp_get("/ngsi-ld/v2/entities", params={"id": id, "limit": 10})
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            return f"Resource '{id}' requires authentication. Use rsp_get_entities_v2 with a token."
        if exc.response.status_code == 404:
            return f"Resource '{id}' not found via RSP."
        raise
    results = data.get("result", data) if isinstance(data, dict) else data
    if not results:
        return f"No data found for resource '{id}' via RSP."
    total = data.get("totalHits", len(results)) if isinstance(data, dict) else len(results)
    return (
        f"RSP entity data for '{id}' ({len(results) if isinstance(results, list) else 1} of {total}):\n"
        + json.dumps(results, indent=2)[:3000]
    )
