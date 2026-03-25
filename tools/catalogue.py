from typing import Any
from ._app import mcp, _get, _post, _put, _patch, _delete, _parse


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
