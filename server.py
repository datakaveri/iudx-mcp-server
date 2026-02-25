import json
import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("IUDX_BASE_URL", "https://v2.dev.controlplane.iudx.io")

mcp = FastMCP("IUDX MCP Server")


# ---------------------------------------------------------------------------
# Internal HTTP helpers
# ---------------------------------------------------------------------------

def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


async def _get(
    path: str, *, token: str = "", params: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("GET %s params=%s", url, params)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, params=params, headers=_headers(token))
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
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(url, params=params, json=body, headers=_headers(token))
        r.raise_for_status()
        return r.json()


async def _put(
    path: str, *, token: str = "", body: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("PUT %s", url)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.put(url, json=body, headers=_headers(token))
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
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.patch(url, params=params, json=body, headers=_headers(token))
        r.raise_for_status()
        return r.json()


async def _delete(
    path: str, *, token: str = "", params: dict[str, Any] | None = None
) -> dict:
    url = f"{BASE_URL}{path}"
    logger.info("DELETE %s params=%s", url, params)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.delete(url, params=params, headers=_headers(token))
        r.raise_for_status()
        return r.json()


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


# ===========================================================================
# TOOLS
# ===========================================================================

# ---------------------------------------------------------------------------
# Catalogue — public reads
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_catalogue(
    search_criteria_json: str,
    filter_fields: list[str] | None = None,
    token: str = "",
    page: int = 1,
    size: int = 20,
    sort: str = "",
) -> dict:
    """Search the IUDX catalogue (POST /iudx/v2/cat/search).

    Only items with publishStatus=ACTIVE and dataUploadStatus=true are returned.
    Supports text search, term/range/temporal criteria, and flattened-field search.

    Args:
        search_criteria_json: JSON string for the search body. Examples:
            Text search: '{"q": "air quality"}'
            Type filter: '{"searchCriteria": [{"searchType": "term", "field": "type",
                           "values": ["adex:DataBank"]}]}'
            Complex: '{"q": "water", "searchCriteria": [{"searchType": "term",
                       "field": "accessPolicy", "values": ["OPEN"]}]}'
        filter_fields: Optional list of field names to project in the response.
        token:         Optional Bearer JWT (for private items).
        page:          Page number, 1-indexed (default 1).
        size:          Results per page — max so that size*(page-1)+size ≤ 10 000 (default 20).
        sort:          Sort expression e.g. "itemCreatedAt:desc;name:asc".
    """
    body = _parse(search_criteria_json, "search_criteria_json")
    if filter_fields:
        body["filter"] = filter_fields
    params: dict = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _post("/iudx/v2/cat/search", token=token, params=params, body=body)


@mcp.tool()
async def get_cat_item(id: str, token: str = "") -> dict:
    """Fetch full metadata for a catalogue item by UUID (GET /iudx/v2/cat/item).

    Auth is optional — required only for restricted or private items.

    Args:
        id:    UUID of the catalogue item (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
        token: Optional Bearer JWT for restricted/private items.
    """
    return await _get("/iudx/v2/cat/item", token=token, params={"id": id})


@mcp.tool()
async def get_cat_item_with_access(
    id: str,
    token: str = "",
    is_delegator: bool = False,
    delegate_id: str = "",
) -> dict:
    """Fetch a catalogue item with access-policy enforcement (GET /iudx/v2/cat/item/access).

    OPEN items are accessible without a token; RESTRICTED items require a token
    and a valid access policy; PRIVATE items are accessible only by the owner
    or an admin.

    Args:
        id:           UUID of the catalogue item.
        token:        Bearer JWT — required for RESTRICTED/PRIVATE items.
        is_delegator: Set True if the caller is acting as a delegator.
        delegate_id:  Delegate DID — required when is_delegator=True.
    """
    params: dict = {"id": id}
    if is_delegator:
        params["isDelegator"] = "true"
        if delegate_id:
            params["did"] = delegate_id
    return await _get("/iudx/v2/cat/item/access", token=token, params=params)


@mcp.tool()
async def count_catalogue_entities(
    search_criteria_json: str = '{"searchCriteria": [{"searchType": "term", "field": "type", "values": ["adex:DataBank", "adex:AiModel", "adex:Apps"]}]}',
    token: str = "",
) -> dict:
    """Count catalogue entities grouped by type (POST /iudx/v2/cat/count).

    Args:
        search_criteria_json: JSON search body. Defaults to counting all three
            entity types (DataBank, AiModel, Apps).
        token: Optional Bearer JWT.
    """
    return await _post("/iudx/v2/cat/count", token=token, body=_parse(search_criteria_json))


@mcp.tool()
async def list_catalogue_filter_values(
    entity_type: str = "adex:DataBank",
    token: str = "",
) -> dict:
    """List available filter values for a given entity type (POST /iudx/v2/cat/list).

    Args:
        entity_type: One of adex:DataBank | adex:AiModel | adex:Apps.
        token:       Optional Bearer JWT.
    """
    filter_map = {
        "adex:DataBank": ["concepts", "tags", "fileFormat", "accessPolicy",
                          "organizationType", "industry"],
        "adex:AiModel":  ["department", "organizationType", "industry",
                          "fileFormat", "accessPolicy", "modelType"],
        "adex:Apps":     ["department", "organizationType"],
    }
    body = {
        "searchCriteria": [{"searchType": "term", "field": "type",
                            "values": [entity_type]}],
        "filter": filter_map.get(entity_type, ["tags", "accessPolicy"]),
    }
    return await _post("/iudx/v2/cat/list", token=token, body=body)


# ---------------------------------------------------------------------------
# Catalogue — authenticated mutations
# ---------------------------------------------------------------------------

@mcp.tool()
async def create_cat_item(item_json: str, token: str) -> dict:
    """Create a new IUDX catalogue item (POST /iudx/v2/cat/item).

    Requires publisher / org_admin / cos_admin role.
    Do NOT include auto-managed fields: itemCreatedAt, itemStatus, publishStatus,
    dataUploadStatus, lastUpdated, ownerUserId — these are set by the server.

    Args:
        item_json: JSON string of the full item body. Must include 'type' array
                   (e.g. ["adex:DataBank"]) and required fields (name, label, etc.).
        token:     Bearer JWT with provider / org_admin / cos_admin role.
    """
    return await _post("/iudx/v2/cat/item", token=token, body=_parse(item_json, "item_json"))


@mcp.tool()
async def update_cat_item(item_json: str, token: str) -> dict:
    """Replace an existing catalogue item (PUT /iudx/v2/cat/item).

    The 'id' field must be present in the payload. The following fields cannot
    be updated via this endpoint: id, type[0], itemStatus, itemCreatedAt,
    publishStatus, dataUploadStatus.

    Args:
        item_json: JSON string of the updated item body (must include 'id').
        token:     Bearer JWT with appropriate role.
    """
    return await _put("/iudx/v2/cat/item", token=token, body=_parse(item_json, "item_json"))


@mcp.tool()
async def delete_cat_item(id: str, token: str) -> dict:
    """Delete a catalogue item by UUID (DELETE /iudx/v2/cat/item).

    Returns HTTP 409 if the item has associated child entities.

    Args:
        id:    UUID of the item to delete.
        token: Bearer JWT with appropriate role.
    """
    return await _delete("/iudx/v2/cat/item", token=token, params={"id": id})


@mcp.tool()
async def patch_org_asset(id: str, patch_json: str, token: str) -> dict:
    """Update publishStatus or dataUploadStatus for an org asset (PATCH /iudx/v2/cat/organisation/asset).

    org_admin / cos_admin can set both fields; provider can only set dataUploadStatus.
    publishStatus values: ACTIVE | PENDING | DECLINED.

    Args:
        id:         UUID of the asset to patch.
        patch_json: JSON string, e.g. '{"publishStatus": "ACTIVE", "dataUploadStatus": true}'.
        token:      Bearer JWT with org_admin / cos_admin / provider role.
    """
    return await _patch(
        "/iudx/v2/cat/organisation/asset",
        token=token, params={"id": id},
        body=_parse(patch_json, "patch_json"),
    )


# ---------------------------------------------------------------------------
# Catalogue — org / admin reads (auth-gated)
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_org_assets(
    token: str,
    page: int = 1,
    size: int = 100,
    sort: str = "",
    filter_myassets: bool = False,
) -> dict:
    """List assets belonging to the authenticated user's organisation (GET /iudx/v2/cat/organisation/asset).

    Requires org_admin role.

    Args:
        token:           Bearer JWT (org_admin).
        page:            Page number (default 1).
        size:            Results per page (default 100).
        sort:            Sort expression e.g. "itemCreatedAt:desc".
        filter_myassets: If True, exclude assets owned by the authenticated user.
    """
    params: dict = {"page": page, "size": size,
                    "filter_myassets": str(filter_myassets).lower()}
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/cat/organisation/asset", token=token, params=params)


@mcp.tool()
async def search_org_assets(
    search_criteria_json: str,
    token: str,
    page: int = 1,
    size: int = 100,
    sort: str = "",
) -> dict:
    """Search organisation assets with filter criteria (POST /iudx/v2/cat/organisation/asset).

    Requires org_admin role.

    Args:
        search_criteria_json: JSON search body e.g.
            '{"searchCriteria": [{"searchType": "term", "field": "publishStatus",
               "values": ["PENDING"]}], "filter": ["id", "name", "publishStatus"]}'
        token: Bearer JWT (org_admin).
        page:  Page number (default 1).
        size:  Results per page (default 100).
        sort:  Sort expression.
    """
    params: dict = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _post(
        "/iudx/v2/cat/organisation/asset",
        token=token, params=params,
        body=_parse(search_criteria_json),
    )


@mcp.tool()
async def get_all_platform_assets(
    token: str,
    page: int = 1,
    size: int = 100,
    sort: str = "",
) -> dict:
    """List all assets across the entire platform (GET /iudx/v2/cat/getAllAssets).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
        page:  Page number (default 1).
        size:  Results per page (default 100).
        sort:  Sort expression.
    """
    params: dict = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/cat/getAllAssets", token=token, params=params)


@mcp.tool()
async def filter_all_platform_assets(
    search_criteria_json: str,
    token: str,
    page: int = 1,
    size: int = 100,
    sort: str = "",
) -> dict:
    """Filter all platform assets with search criteria (POST /iudx/v2/cat/getAllAssets).

    Requires cos_admin role.

    Args:
        search_criteria_json: JSON search body (same format as search_catalogue).
        token: Bearer JWT (cos_admin).
        page:  Page number (default 1).
        size:  Results per page (default 100).
        sort:  Sort expression.
    """
    params: dict = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _post(
        "/iudx/v2/cat/getAllAssets",
        token=token, params=params,
        body=_parse(search_criteria_json),
    )


@mcp.tool()
async def get_my_assets(
    token: str,
    page: int = 1,
    size: int = 10,
    sort: str = "",
) -> dict:
    """Fetch the authenticated user's own catalogue assets (GET /iudx/v2/cat/search/myassets).

    Filters by ownerUserId from the token. Ignores publishStatus / dataUploadStatus.

    Args:
        token: Bearer JWT.
        page:  Page number (default 1).
        size:  Results per page (default 10).
        sort:  Sort expression.
    """
    params: dict = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/cat/search/myassets", token=token, params=params)


@mcp.tool()
async def search_my_assets(
    search_criteria_json: str,
    token: str,
    page: int = 1,
    size: int = 10,
) -> dict:
    """Search within the authenticated user's own assets (POST /iudx/v2/cat/search/myassets).

    Automatically scoped to ownerUserId from the token.

    Args:
        search_criteria_json: JSON search body (same format as search_catalogue).
        token: Bearer JWT.
        page:  Page number (default 1).
        size:  Results per page (default 10).
    """
    return await _post(
        "/iudx/v2/cat/search/myassets",
        token=token, params={"page": page, "size": size},
        body=_parse(search_criteria_json),
    )


# ---------------------------------------------------------------------------
# Resource Servers
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_resource_servers(token: str) -> dict:
    """List all registered IUDX resource servers (GET /iudx/v2/resource_servers).

    Args:
        token: Bearer JWT with cos_admin / org_admin role.
    """
    return await _get("/iudx/v2/resource_servers", token=token)


@mcp.tool()
async def create_resource_server(server_json: str, token: str) -> dict:
    """Register a new IUDX resource server (POST /iudx/v2/resource_servers).

    Args:
        server_json: JSON string e.g.
            '{"name": "My RS", "url": "rs.example.org", "type": "file testing",
              "visibility": "PUBLIC", "query_type": ["ATTR"], "injection_type": "api"}'
        token: Bearer JWT with cos_admin / org_admin role.
    """
    return await _post(
        "/iudx/v2/resource_servers", token=token,
        body=_parse(server_json, "server_json"),
    )


@mcp.tool()
async def get_resource_server(id: str, token: str) -> dict:
    """Fetch a resource server by ID (GET /iudx/v2/resource_servers/{id}).

    Args:
        id:    Resource server UUID.
        token: Bearer JWT with cos_admin / org_admin role.
    """
    return await _get(f"/iudx/v2/resource_servers/{id}", token=token)


@mcp.tool()
async def delete_resource_server(id: str, token: str) -> dict:
    """Delete a resource server by ID (DELETE /iudx/v2/resource_servers/{id}).

    Args:
        id:    Resource server UUID.
        token: Bearer JWT with cos_admin / org_admin role.
    """
    return await _delete(f"/iudx/v2/resource_servers/{id}", token=token)


# ---------------------------------------------------------------------------
# Organisations
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_organisations(token: str) -> dict:
    """List all organisations on the platform (GET /iudx/v2/auth/organisations).

    Args:
        token: Bearer JWT with cos_admin / org_admin role.
    """
    return await _get("/iudx/v2/auth/organisations", token=token)


@mcp.tool()
async def get_organisation(id: str, token: str = "") -> dict:
    """Fetch details of a specific organisation by ID (GET /iudx/v2/auth/organisations/{id}).

    Args:
        id:    Organisation UUID.
        token: Optional Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/organisations/{id}", token=token)


@mcp.tool()
async def list_org_users(org_id: str, token: str = "") -> dict:
    """List users who are members of an organisation (GET /iudx/v2/auth/organisations/{id}/users).

    Args:
        org_id: Organisation UUID.
        token:  Optional Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/organisations/{org_id}/users", token=token)


@mcp.tool()
async def list_org_creation_requests(token: str) -> dict:
    """List pending organisation creation requests (GET /iudx/v2/auth/organisations/requests).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
    """
    return await _get("/iudx/v2/auth/organisations/requests", token=token)


@mcp.tool()
async def submit_org_creation_request(request_json: str, token: str) -> dict:
    """Submit a new organisation creation request (POST /iudx/v2/auth/organisations/requests).

    Args:
        request_json: JSON string with org details (name, entity_type, org_sector,
                      website_link, address, certificate_path, etc.).
        token:        Bearer JWT (authenticated user).
    """
    return await _post(
        "/iudx/v2/auth/organisations/requests",
        token=token, body=_parse(request_json, "request_json"),
    )


@mcp.tool()
async def approve_org_creation_request(
    request_id: str,
    action: str,
    token: str,
) -> dict:
    """Approve or reject an organisation creation request (POST /iudx/v2/auth/organisations/requests/approve).

    Requires cos_admin role.

    Args:
        request_id: UUID of the org creation request.
        action:     "approve" or "reject".
        token:      Bearer JWT (cos_admin).
    """
    return await _post(
        "/iudx/v2/auth/organisations/requests/approve",
        token=token,
        body={"requestId": request_id, "action": action},
    )


@mcp.tool()
async def list_org_join_requests(org_id: str, token: str) -> dict:
    """List pending join requests for an organisation (GET /iudx/v2/auth/organisations/{id}/join_requests).

    Requires org_admin role.

    Args:
        org_id: Organisation UUID.
        token:  Bearer JWT (org_admin).
    """
    return await _get(
        f"/iudx/v2/auth/organisations/{org_id}/join_requests", token=token
    )


@mcp.tool()
async def handle_org_join_request(
    org_id: str,
    req_id: str,
    action: str,
    token: str,
) -> dict:
    """Approve or reject an organisation join request (POST /iudx/v2/auth/organisations/{org_id}/join_requests/{req_id}).

    Requires org_admin role.

    Args:
        org_id:  Organisation UUID.
        req_id:  Join request UUID.
        action:  "approve" or "reject".
        token:   Bearer JWT (org_admin).
    """
    return await _post(
        f"/iudx/v2/auth/organisations/{org_id}/join_requests/{req_id}",
        token=token, body={"action": action},
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_my_profile(token: str) -> dict:
    """Fetch the authenticated user's own profile (GET /iudx/v2/auth/user).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user", token=token)


@mcp.tool()
async def update_my_profile(profile_json: str, token: str) -> dict:
    """Update the authenticated user's profile (PUT /iudx/v2/auth/user/update).

    Args:
        profile_json: JSON string of profile fields to update.
        token:        Bearer JWT.
    """
    return await _put(
        "/iudx/v2/auth/user/update", token=token,
        body=_parse(profile_json, "profile_json"),
    )


@mcp.tool()
async def admin_list_users(token: str) -> dict:
    """Admin: list all users on the platform (GET /iudx/v2/auth/admin/user).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
    """
    return await _get("/iudx/v2/auth/admin/user", token=token)


@mcp.tool()
async def admin_get_user(id: str, token: str) -> dict:
    """Admin: fetch a specific user by ID (GET /iudx/v2/auth/admin/user/{id}).

    Requires cos_admin role.

    Args:
        id:    User UUID.
        token: Bearer JWT (cos_admin).
    """
    return await _get(f"/iudx/v2/auth/admin/user/{id}", token=token)


# ---------------------------------------------------------------------------
# Credits
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_credit_balance(token: str) -> dict:
    """Fetch the authenticated user's credit balance (GET /iudx/v2/auth/user/credit/balance).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/credit/balance", token=token)


@mcp.tool()
async def request_credits(request_json: str, token: str) -> dict:
    """Submit a credit top-up request (POST /iudx/v2/auth/user/credit/request).

    Args:
        request_json: JSON string with credit request details e.g. '{"amount": 100}'.
        token:        Bearer JWT.
    """
    return await _post(
        "/iudx/v2/auth/user/credit/request",
        token=token, body=_parse(request_json, "request_json"),
    )


@mcp.tool()
async def get_credit_request(id: str, token: str) -> dict:
    """Fetch a specific credit request by ID (GET /iudx/v2/auth/user/credit/request/{id}).

    Args:
        id:    Credit request UUID.
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/user/credit/request/{id}", token=token)


@mcp.tool()
async def admin_list_credit_requests(token: str) -> dict:
    """Admin: list all credit requests on the platform (GET /iudx/v2/auth/credit/request).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
    """
    return await _get("/iudx/v2/auth/credit/request", token=token)


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_token(credentials_json: str) -> dict:
    """Obtain or refresh an IUDX platform JWT token (POST /iudx/v2/auth/token).

    No prior auth needed. Returns a Bearer JWT in the 'token' field.
    The returned token can be passed to all other tools that accept a 'token' arg.

    Args:
        credentials_json: JSON string with login credentials or refresh token body.
    """
    return await _post(
        "/iudx/v2/auth/token",
        body=_parse(credentials_json, "credentials_json"),
    )


# ---------------------------------------------------------------------------
# Dashboard & Auditing
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_usage_summary() -> dict:
    """Fetch platform-wide usage metrics (GET /iudx/v2/dashboard/usage-summary).

    No authentication required.
    """
    return await _get("/iudx/v2/dashboard/usage-summary")


@mcp.tool()
async def get_consumer_activity(
    token: str,
    asset_type: str = "",
    access_policy: str = "",
    action: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 1,
    size: int = 20,
) -> dict:
    """Fetch the authenticated consumer's activity logs (GET /iudx/v2/auditing/consumer/activity).

    Args:
        token:         Bearer JWT.
        asset_type:    Filter: DATABANK | AI_MODEL | USECASE.
        access_policy: Filter: OPEN | RESTRICTED | PRIVATE | PII.
        action:        Filter: View | Download | Upload | Update | Delete.
        time:          ISO-8601 start timestamp.
        end_time:      ISO-8601 end timestamp.
        timerel:       between | before | after.
        page:          Page number (default 1).
        size:          Results per page (default 20).
    """
    params: dict = {"page": page, "size": size}
    for k, v in [("assetType", asset_type), ("accessPolicy", access_policy),
                 ("action", action), ("time", time), ("endtime", end_time),
                 ("timerel", timerel)]:
        if v:
            params[k] = v
    return await _get("/iudx/v2/auditing/consumer/activity", token=token, params=params)


@mcp.tool()
async def admin_get_activity_logs(
    token: str,
    asset_type: str = "",
    access_policy: str = "",
    action: str = "",
    org_id: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 1,
    size: int = 20,
) -> dict:
    """Admin: fetch all platform activity logs (GET /iudx/v2/auditing/admin/activity).

    Requires cos_admin role.

    Args:
        token:         Bearer JWT (cos_admin).
        asset_type:    Filter: DATABANK | AI_MODEL | USECASE.
        access_policy: Filter: OPEN | RESTRICTED | PRIVATE | PII.
        action:        Filter: View | Download | Upload | Update | Delete.
        org_id:        Filter by organisation UUID.
        time:          ISO-8601 start timestamp.
        end_time:      ISO-8601 end timestamp.
        timerel:       between | before | after.
        page:          Page number (default 1).
        size:          Results per page (default 20).
    """
    params: dict = {"page": page, "size": size}
    for k, v in [("assetType", asset_type), ("accessPolicy", access_policy),
                 ("action", action), ("orgId", org_id), ("time", time),
                 ("endtime", end_time), ("timerel", timerel)]:
        if v:
            params[k] = v
    return await _get("/iudx/v2/auditing/admin/activity", token=token, params=params)


# ---------------------------------------------------------------------------
# Leaderboard (public)
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_asset_leaderboard() -> dict:
    """Fetch the IUDX asset leaderboard (GET /iudx/v2/leaderboard/asset).

    No authentication required.
    """
    return await _get("/iudx/v2/leaderboard/asset")


@mcp.tool()
async def get_provider_leaderboard() -> dict:
    """Fetch the IUDX provider leaderboard (GET /iudx/v2/leaderboard/provider).

    No authentication required.
    """
    return await _get("/iudx/v2/leaderboard/provider")


@mcp.tool()
async def get_org_leaderboard() -> dict:
    """Fetch the IUDX organisation leaderboard (GET /iudx/v2/leaderboard/organization).

    No authentication required.
    """
    return await _get("/iudx/v2/leaderboard/organization")


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_subscriptions(token: str) -> dict:
    """List all subscriptions for the authenticated user (GET /iudx/v2/subscriptions).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/subscriptions", token=token)


@mcp.tool()
async def create_subscription(subscription_json: str, token: str) -> dict:
    """Create a new data subscription (POST /iudx/v2/subscriptions).

    Args:
        subscription_json: JSON string with subscription definition.
        token:             Bearer JWT.
    """
    return await _post(
        "/iudx/v2/subscriptions", token=token,
        body=_parse(subscription_json, "subscription_json"),
    )


@mcp.tool()
async def get_subscription(id: str, token: str) -> dict:
    """Fetch a subscription by ID (GET /iudx/v2/subscriptions/{id}).

    Args:
        id:    Subscription UUID.
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/subscriptions/{id}", token=token)


@mcp.tool()
async def update_subscription(id: str, subscription_json: str, token: str) -> dict:
    """Update an existing subscription (PUT /iudx/v2/subscriptions/{id}).

    Args:
        id:                Subscription UUID.
        subscription_json: JSON string with updated subscription fields.
        token:             Bearer JWT.
    """
    return await _put(
        f"/iudx/v2/subscriptions/{id}", token=token,
        body=_parse(subscription_json, "subscription_json"),
    )


@mcp.tool()
async def delete_subscription(id: str, token: str) -> dict:
    """Delete a subscription by ID (DELETE /iudx/v2/subscriptions/{id}).

    Args:
        id:    Subscription UUID.
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/subscriptions/{id}", token=token)


# ---------------------------------------------------------------------------
# Asset Access Requests
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_asset_access_requests(token: str) -> dict:
    """List asset access requests for the authenticated user (GET /iudx/v2/auth/asset/request).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/asset/request", token=token)


@mcp.tool()
async def create_asset_access_request(request_json: str, token: str) -> dict:
    """Submit a new asset access request (POST /iudx/v2/auth/asset/request).

    Args:
        request_json: JSON string with the access request body.
        token:        Bearer JWT.
    """
    return await _post(
        "/iudx/v2/auth/asset/request", token=token,
        body=_parse(request_json, "request_json"),
    )


@mcp.tool()
async def get_asset_access_request(id: str, token: str) -> dict:
    """Fetch a specific asset access request by ID (GET /iudx/v2/auth/asset/request/{id}).

    Args:
        id:    Access request UUID.
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/asset/request/{id}", token=token)


@mcp.tool()
async def update_asset_access_request(id: str, update_json: str, token: str) -> dict:
    """Update an asset access request (PUT /iudx/v2/auth/asset/request/{id}).

    Args:
        id:          Access request UUID.
        update_json: JSON string with updated fields.
        token:       Bearer JWT.
    """
    return await _put(
        f"/iudx/v2/auth/asset/request/{id}", token=token,
        body=_parse(update_json, "update_json"),
    )


@mcp.tool()
async def delete_asset_access_request(id: str, token: str) -> dict:
    """Delete / cancel an asset access request (DELETE /iudx/v2/auth/asset/request/{id}).

    Args:
        id:    Access request UUID.
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/asset/request/{id}", token=token)


# ---------------------------------------------------------------------------
# Compute Requests
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_my_compute_requests(token: str) -> dict:
    """List the authenticated user's own compute requests (GET /iudx/v2/auth/user/compute/requests).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/compute/requests", token=token)


@mcp.tool()
async def get_compute_request(id: str, token: str) -> dict:
    """Fetch a specific compute request by ID (GET /iudx/v2/auth/user/compute/requests/{id}).

    Args:
        id:    Compute request UUID.
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/user/compute/requests/{id}", token=token)


@mcp.tool()
async def admin_list_compute_requests(token: str) -> dict:
    """Admin: list all compute requests across all users (GET /iudx/v2/auth/compute/requests).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
    """
    return await _get("/iudx/v2/auth/compute/requests", token=token)


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


# ===========================================================================
# PROMPTS — reusable multi-step workflow templates
# ===========================================================================

@mcp.prompt()
def explore_dataset(id: str = "") -> str:
    """Explore one specific dataset or summarise all available datasets.

    Args:
        id: Optional UUID. If omitted, summarises all datasets from the catalogue.
    """
    if id:
        return (
            f"Fetch full metadata for IUDX catalogue item '{id}' using get_cat_item. "
            "Explain: name, type, description, organisation, access policy, tags, "
            "data readiness score (if present), and creation date. "
            "If the item is not OPEN, note any access requirements."
        )
    return (
        "Read the iudx://catalogue/datasets resource to get the list of available "
        "DataBank datasets. Also read iudx://catalogue/ai_models and "
        "iudx://catalogue/apps. Summarise: total counts per type, top 5 datasets "
        "by name with their organisation and access policy."
    )


@mcp.prompt()
def find_datasets_by_topic(
    topic: str,
    item_type: str = "adex:DataBank",
) -> str:
    """Search the IUDX catalogue for items related to a topic.

    Args:
        topic:     Free-text description of the domain (e.g. "air quality in Pune").
        item_type: Catalogue type to search in: adex:DataBank | adex:AiModel | adex:Apps.
    """
    return (
        f"Search the IUDX catalogue for {item_type} items related to '{topic}'. "
        f"Use search_catalogue with search_criteria_json = "
        f'\'{{\"q\": \"{topic}\", \"searchCriteria\": [{{"searchType": "term", '
        f'"field": "type", "values": ["{item_type}"]}}]}}\'. '
        "List the results: ID, name, organisation, access policy, and a one-line "
        "description for each. Mention the total number of matches."
    )


@mcp.prompt()
def platform_health_summary() -> str:
    """Produce an executive summary of the current state of the IUDX platform."""
    return (
        "Generate a platform health report for IUDX using these steps:\n"
        "1. Call count_catalogue_entities (default args) — report DataBank, AiModel, Apps totals.\n"
        "2. Read iudx://dashboard/usage_summary — highlight key usage metrics.\n"
        "3. Read iudx://leaderboard/assets — list top 5 assets.\n"
        "4. Read iudx://leaderboard/providers — list top 5 providers.\n"
        "5. Read iudx://leaderboard/organizations — list top 5 organisations.\n"
        "Present all findings as a structured executive report with sections."
    )


@mcp.prompt()
def request_dataset_access(asset_id: str) -> str:
    """Walk through requesting access to a restricted IUDX dataset.

    Args:
        asset_id: UUID of the restricted catalogue item.
    """
    return (
        f"I want to access the IUDX dataset '{asset_id}'. Please:\n"
        "1. Call get_cat_item_with_access with this id to determine the access policy.\n"
        "2. If the policy is OPEN, confirm the dataset is directly accessible.\n"
        "3. If RESTRICTED or PRIVATE, call create_asset_access_request with the "
        "appropriate request body to submit an access request. "
        "Report the request ID and next steps."
    )


@mcp.prompt()
def onboard_as_provider(item_json_hint: str = "") -> str:
    """Guide a data provider through the full item publication workflow.

    Args:
        item_json_hint: Optional partial JSON the user has already drafted.
    """
    hint = (
        f"The user has provided this partial item JSON as a starting point:\n{item_json_hint}\n"
        if item_json_hint else ""
    )
    return (
        f"{hint}Help the user publish a new dataset on IUDX. Steps:\n"
        "1. If no token is available, call get_token with their credentials.\n"
        "2. Call list_catalogue_filter_values for adex:DataBank to show valid tags, "
        "concepts, and other metadata options.\n"
        "3. Help the user construct a valid item JSON payload.\n"
        "4. Call create_cat_item with the payload and token.\n"
        "5. After creation, call patch_org_asset to set publishStatus=ACTIVE "
        "(if user has org_admin role) or advise them to request approval.\n"
        "Report the new item's ID and its current publication status."
    )


@mcp.prompt()
def audit_my_usage(start_time: str = "", end_time: str = "") -> str:
    """Review personal API usage for a given time window.

    Args:
        start_time: Optional ISO-8601 start (e.g. "2025-01-01T00:00:00Z").
        end_time:   Optional ISO-8601 end timestamp.
    """
    time_note = (
        f" Filter the time range from {start_time} to {end_time}."
        if start_time else ""
    )
    return (
        f"Retrieve my IUDX activity logs using get_consumer_activity.{time_note} "
        "Analyse the results and report:\n"
        "- Total number of activities.\n"
        "- Breakdown by action type (View, Download, Upload, etc.).\n"
        "- Most frequently accessed datasets (by asset ID).\n"
        "- Any access policy anomalies (e.g. RESTRICTED accesses)."
    )


@mcp.prompt()
def manage_organisation(org_id: str = "") -> str:
    """Perform organisation management tasks.

    Args:
        org_id: Optional UUID. If omitted, list all organisations first.
    """
    if org_id:
        return (
            f"Manage IUDX organisation '{org_id}'. Using the provided token:\n"
            "1. Call get_organisation to show current details.\n"
            "2. Call list_org_users to list current members.\n"
            "3. Call list_org_join_requests to show any pending join requests.\n"
            "4. For each pending join request, ask whether to approve or reject, "
            "then call handle_org_join_request accordingly.\n"
            "Present a summary of the organisation's current state."
        )
    return (
        "List all IUDX organisations using list_organisations. "
        "For each organisation, show its ID, name, and member count if available. "
        "Ask the user which organisation they want to manage, then repeat with that org_id."
    )


@mcp.prompt()
def subscribe_to_dataset(asset_id: str) -> str:
    """Set up a data subscription for a catalogue asset.

    Args:
        asset_id: UUID of the catalogue item to subscribe to.
    """
    return (
        f"Set up a subscription for IUDX dataset '{asset_id}'. Steps:\n"
        "1. Call get_cat_item to confirm the asset exists and note its access policy.\n"
        "2. If access policy is not OPEN, call get_cat_item_with_access to verify "
        "the user has access.\n"
        "3. Call create_subscription with a subscription body referencing this asset_id.\n"
        "4. Return the new subscription ID and any delivery configuration details."
    )


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    logger.info(
        "Starting IUDX MCP Server — transport=%s base_url=%s", transport, BASE_URL
    )
    if transport in ("sse", "streamable-http"):
        mcp.run(transport=transport, host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
