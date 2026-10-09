"""Additional control-plane tools, covering the rest of control-plane-2.0.yml."""
from ._app import (
    mcp, _get, _post, _put, _patch, _delete, _get_text, _parse,
)


@mcp.tool()
async def create_app(
    body_json: str,
    token: str,
) -> dict:
    """Create an app (client credentials for an app) with delegated roles (POST /iudx/v2/auth/app).

    Args:
        body_json: JSON string, e.g. '{"expiryAt": "2026-12-31T23:59:59", "roles": [{"role": "consumer",
                    "constraints": [{"scope": "data-access", "entityId": ["<uuid>"], "entityType": "DATABANK"}]}]}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/app", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_apps(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List the authenticated user's apps (GET /iudx/v2/auth/app).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/auth/app", token=token, params=params)



@mcp.tool()
async def delete_app(
    appId: str,
    token: str,
) -> dict:
    """Delete an app (DELETE /iudx/v2/auth/app/{appId}).

    Args:
        appId: Path parameter `appId` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/app/{appId}", token=token)



@mcp.tool()
async def update_app_status(
    appId: str,
    status: str,
    token: str,
) -> dict:
    """Update an app's status (PATCH /iudx/v2/auth/app/{appId}).

    Args:
        appId: Path parameter `appId` (UUID unless noted).
        status: Query parameter `status` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["status"] = status
    return await _patch(f"/iudx/v2/auth/app/{appId}", token=token, params=params)



@mcp.tool()
async def get_jwks() -> dict:
    """Fetch the platform JSON Web Key Set (public keys for validating tokens) (GET /iudx/v2/auth/jwks).
    """
    return await _get("/iudx/v2/auth/jwks")



@mcp.tool()
async def get_app_token(body_json: str) -> dict:
    """Obtain a token for an app using its appId/appSecret (optionally scoped to an item) (POST /iudx/auth/v2/app/token).

    Args:
        body_json: JSON string, e.g. '{"appId": "<uuid>", "appSecret": "<secret>", "itemId": "<optional uuid>"}'
    """
    return await _post("/iudx/auth/v2/app/token", body=_parse(body_json, "body_json"))



@mcp.tool()
async def create_client_credentials(token: str) -> dict:
    """Create a new clientId/clientSecret pair for the authenticated user (POST /iudx/v2/auth/client).

    Args:
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/client", token=token)



@mcp.tool()
async def download_admin_activity_report(
    token: str,
    user_id: str = "",
    asset_type: str = "",
    access_policy: str = "",
    action: str = "",
    log_type: str = "",
    sandbox_type: str = "",
    org_id: str = "",
    delegate_id: str = "",
    actor_type: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """Download the admin activity report as CSV (GET /iudx/v2/auditing/reportactivity/admin).

    Args:
        token: Bearer JWT.
        user_id: Query parameter `userId` (optional).
        asset_type: Query parameter `assetType` (optional).
        access_policy: Query parameter `accessPolicy` (optional).
        action: Query parameter `action` (optional).
        log_type: Query parameter `logType` (optional).
        sandbox_type: Query parameter `sandboxType` (optional).
        org_id: Query parameter `orgId` (optional).
        delegate_id: Query parameter `delegateId` (optional).
        actor_type: Query parameter `actorType` (optional).
        time: Query parameter `time` (optional).
        end_time: Query parameter `endtime` (optional).
        timerel: Query parameter `timerel` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if user_id:
        params["userId"] = user_id
    if asset_type:
        params["assetType"] = asset_type
    if access_policy:
        params["accessPolicy"] = access_policy
    if action:
        params["action"] = action
    if log_type:
        params["logType"] = log_type
    if sandbox_type:
        params["sandboxType"] = sandbox_type
    if org_id:
        params["orgId"] = org_id
    if delegate_id:
        params["delegateId"] = delegate_id
    if actor_type:
        params["actorType"] = actor_type
    if time:
        params["time"] = time
    if end_time:
        params["endtime"] = end_time
    if timerel:
        params["timerel"] = timerel
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get_text("/iudx/v2/auditing/reportactivity/admin", token=token, params=params)



@mcp.tool()
async def download_consumer_activity_report(
    token: str,
    asset_type: str = "",
    access_policy: str = "",
    action: str = "",
    log_type: str = "",
    sandbox_type: str = "",
    org_id: str = "",
    delegate_id: str = "",
    actor_type: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """Download the consumer activity report as CSV (GET /iudx/v2/auditing/reportactivity/consumer).

    Args:
        token: Bearer JWT.
        asset_type: Query parameter `assetType` (optional).
        access_policy: Query parameter `accessPolicy` (optional).
        action: Query parameter `action` (optional).
        log_type: Query parameter `logType` (optional).
        sandbox_type: Query parameter `sandboxType` (optional).
        org_id: Query parameter `orgId` (optional).
        delegate_id: Query parameter `delegateId` (optional).
        actor_type: Query parameter `actorType` (optional).
        time: Query parameter `time` (optional).
        end_time: Query parameter `endtime` (optional).
        timerel: Query parameter `timerel` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if asset_type:
        params["assetType"] = asset_type
    if access_policy:
        params["accessPolicy"] = access_policy
    if action:
        params["action"] = action
    if log_type:
        params["logType"] = log_type
    if sandbox_type:
        params["sandboxType"] = sandbox_type
    if org_id:
        params["orgId"] = org_id
    if delegate_id:
        params["delegateId"] = delegate_id
    if actor_type:
        params["actorType"] = actor_type
    if time:
        params["time"] = time
    if end_time:
        params["endtime"] = end_time
    if timerel:
        params["timerel"] = timerel
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get_text("/iudx/v2/auditing/reportactivity/consumer", token=token, params=params)



@mcp.tool()
async def patch_cat_item(
    body_json: str,
    id: str,
    token: str,
) -> dict:
    """Partially update a catalogue item (PATCH /iudx/v2/cat/item).

    Args:
        body_json: JSON object with the fields to patch.
        id: Query parameter `id` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["id"] = id
    return await _patch("/iudx/v2/cat/item", token=token, params=params, body=_parse(body_json, "body_json"))



@mcp.tool()
async def download_item_script(
    filename: str,
    token: str = "",
) -> dict:
    """Download a catalogue item's Python script (GET /items/scripts/download/{filename}).

    Args:
        filename: Path parameter `filename` (UUID unless noted).
        token: Bearer JWT (optional).
    """
    return await _get_text(f"/items/scripts/download/{filename}", token=token)



@mcp.tool()
async def check_item_name_available(
    name: str,
    token: str,
) -> dict:
    """Check whether a catalogue item name is available (GET /iudx/v2/cat/item/available-name).

    Args:
        name: Query parameter `name` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["name"] = name
    return await _get("/iudx/v2/cat/item/available-name", token=token, params=params)



@mcp.tool()
async def create_compute_request(
    body_json: str,
    token: str,
) -> dict:
    """Request compute-role access (POST /iudx/v2/auth/compute/requests).

    Args:
        body_json: JSON string, e.g. '{"additionalInfo": {"purpose": "research"}}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/compute/requests", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_compute_request(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Grant or reject a compute request (admin) (PUT /iudx/v2/auth/compute/requests/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "granted"}' (granted | rejected)
        token: Bearer JWT (cos_admin).
    """
    return await _put(f"/iudx/v2/auth/compute/requests/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def delete_compute_request(
    id: str,
    token: str,
) -> dict:
    """Delete / cancel one of your own compute requests (DELETE /iudx/v2/auth/user/compute/requests/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/user/compute/requests/{id}", token=token)



@mcp.tool()
async def download_compute_requests_report(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
    status: str = "",
) -> dict:
    """Admin: download compute requests report as CSV (GET /iudx/v2/auth/compute/requests/report).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
        status: Query parameter `status` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    if status:
        params["status"] = status
    return await _get_text("/iudx/v2/auth/compute/requests/report", token=token, params=params)



@mcp.tool()
async def admin_get_user_credit_balance(
    id: str,
    token: str,
) -> dict:
    """Admin: fetch a user's credit balance (GET /iudx/v2/auth/admin/user/credit/balance/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT (cos_admin).
    """
    return await _get(f"/iudx/v2/auth/admin/user/credit/balance/{id}", token=token)



@mcp.tool()
async def delete_credit_request(
    id: str,
    token: str,
) -> dict:
    """Delete / cancel one of your own credit requests (DELETE /iudx/v2/auth/user/credit/request/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/user/credit/request/{id}", token=token)



@mcp.tool()
async def admin_handle_credit_request(
    body_json: str,
    token: str,
) -> dict:
    """Admin: grant or reject a credit request (PUT /iudx/v2/auth/credit/request).

    Requires cos_admin role.

    Args:
        body_json: JSON string, e.g. grant:  '{"id": "<uuid>", "status": "granted", "amount": 100, "expiration_date": "2026-12-31T23:59:59"}'
                   reject: '{"id": "<uuid>", "status": "rejected"}'
        token: Bearer JWT (cos_admin).
    """
    return await _put("/iudx/v2/auth/credit/request", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def admin_deduct_user_credits(
    body_json: str,
    token: str,
) -> dict:
    """Admin: deduct credits from a user (PUT /iudx/v2/auth/admin/user/credit/deduct).

    Requires cos_admin role.

    Args:
        body_json: JSON string, e.g. '{"user_id": "<uuid>", "amount": 10, "requested_at": "2026-01-01T00:00:00"}'
        token: Bearer JWT (cos_admin).
    """
    return await _put("/iudx/v2/auth/admin/user/credit/deduct", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def admin_add_user_credits(
    body_json: str,
    token: str,
) -> dict:
    """Admin: add credits to a user (PUT /iudx/v2/auth/admin/user/credit/add).

    Requires cos_admin role.

    Args:
        body_json: JSON string, e.g. '{"user_id": "<uuid>", "amount": 10, "requested_at": "2026-01-01T00:00:00"}'
        token: Bearer JWT (cos_admin).
    """
    return await _put("/iudx/v2/auth/admin/user/credit/add", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def download_credit_requests_report(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
    status: str = "",
) -> dict:
    """Admin: download credit requests report as CSV (GET /iudx/v2/auth/credit/request/report).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
        status: Query parameter `status` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    if status:
        params["status"] = status
    return await _get_text("/iudx/v2/auth/credit/request/report", token=token, params=params)



@mcp.tool()
async def create_delegation(
    body_json: str,
    token: str,
) -> dict:
    """Grant a delegation to another user (POST /iudx/v2/auth/delegation).

    Args:
        body_json: JSON string, e.g. '{"delegateId": "<uuid>", "justification": "...", "expiryAt": "2026-12-31T23:59:59",
                     "roles": [{"role": "consumer", "constraints": [{"scope": "data-access"}]}]}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/delegation", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_delegations_as_delegate(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List delegations granted to you (you are the delegate) (GET /iudx/v2/auth/delegation/delegate).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/auth/delegation/delegate", token=token, params=params)



@mcp.tool()
async def list_delegations_as_delegator(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List delegations you have granted (you are the delegator) (GET /iudx/v2/auth/delegation/delegator).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/auth/delegation/delegator", token=token, params=params)



@mcp.tool()
async def download_delegations_report(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """Download the delegator delegations report as CSV (GET /iudx/v2/auth/delegation/delegator/report).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get_text("/iudx/v2/auth/delegation/delegator/report", token=token, params=params)



@mcp.tool()
async def get_delegation(
    id: str,
    token: str,
) -> dict:
    """Fetch a delegation grant by ID (GET /iudx/v2/auth/delegation/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/delegation/{id}", token=token)



@mcp.tool()
async def delete_delegation(
    id: str,
    token: str,
) -> dict:
    """Delete a delegation grant (delegator only; marks it DELETED) (PUT /iudx/v2/auth/delegation/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _put(f"/iudx/v2/auth/delegation/{id}", token=token)



@mcp.tool()
async def add_delegation_constraints(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Add role constraints to a delegation (PATCH /iudx/v2/auth/delegation/{id}/constraints).

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"roles": [{"role": "consumer", "constraints": [{"scope": "data-access"}]}]}'
        token: Bearer JWT.
    """
    return await _patch(f"/iudx/v2/auth/delegation/{id}/constraints", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def remove_delegation_constraints(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Remove role constraints from a delegation (DELETE /iudx/v2/auth/delegation/{id}/constraints).

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"roles": [{"role": "consumer", "constraints": [{"scope": "data-access"}]}]}'
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/delegation/{id}/constraints", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def reject_delegation(
    id: str,
    token: str,
) -> dict:
    """Reject a delegation granted to you (delegate only) (POST /iudx/v2/auth/delegation/{id}/reject).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _post(f"/iudx/v2/auth/delegation/{id}/reject", token=token)



@mcp.tool()
async def create_user_interaction(
    body_json: str,
    token: str,
) -> dict:
    """Record a user interaction (bookmark / like / dislike) on an asset (POST /iudx/v2/user/interactions).

    Args:
        body_json: JSON string, e.g. '{"assetId": "<uuid>", "assetType": "DATABANK", "actionType": "LIKE"}'
                   assetType: DATABANK | AI_MODEL | USECASE; actionType: BOOKMARK | UNBOOKMARK | LIKE | DISLIKE | NEUTRAL
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/user/interactions", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_user_interactions(
    token: str,
    asset_id: str = "",
    asset_type: str = "",
    action_type: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List the user's interactions (GET /iudx/v2/user/interactions).

    Args:
        token: Bearer JWT.
        asset_id: Query parameter `assetId` (optional).
        asset_type: Query parameter `assetType` (optional).
        action_type: Query parameter `actionType` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if asset_id:
        params["assetId"] = asset_id
    if asset_type:
        params["assetType"] = asset_type
    if action_type:
        params["actionType"] = action_type
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/user/interactions", token=token, params=params)



@mcp.tool()
async def sync_user_interactions(token: str) -> dict:
    """Sync the user's interactions (GET /iudx/v2/user/interactions/sync).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/user/interactions/sync", token=token)



@mcp.tool()
async def create_user_feedback(
    body_json: str,
    token: str,
) -> dict:
    """Submit feedback / a rating for an asset (POST /iudx/v2/user/feedback).

    Args:
        body_json: JSON string, e.g. '{"assetId": "<uuid>", "assetType": "DATABANK", "entityRating": 4,
                   "actionSubtype": "...", "actionSubdata": {}}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/user/feedback", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_user_feedback(
    body_json: str,
    token: str,
) -> dict:
    """Update your feedback / rating for an asset (PUT /iudx/v2/user/feedback).

    Args:
        body_json: JSON string, e.g. '{"assetId": "<uuid>", "assetType": "DATABANK", "entityRating": 4,
                   "actionSubtype": "...", "actionSubdata": {}}'
        token: Bearer JWT.
    """
    return await _put("/iudx/v2/user/feedback", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def delete_user_feedback(
    asset_id: str,
    token: str,
) -> dict:
    """Delete your feedback for an asset (DELETE /iudx/v2/user/feedback).

    Args:
        asset_id: Query parameter `assetId` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["assetId"] = asset_id
    return await _delete("/iudx/v2/user/feedback", token=token, params=params)



@mcp.tool()
async def list_approved_feedback(
    token: str,
    asset_id: str = "",
    action_subtype: str = "",
    rating: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List approved feedback (GET /iudx/v2/user/feedback/approved).

    Args:
        token: Bearer JWT.
        asset_id: Query parameter `assetId` (optional).
        action_subtype: Query parameter `actionSubtype` (optional).
        rating: Query parameter `rating` (optional).
        time: Query parameter `time` (optional).
        end_time: Query parameter `endtime` (optional).
        timerel: Query parameter `timerel` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if asset_id:
        params["assetId"] = asset_id
    if action_subtype:
        params["actionSubtype"] = action_subtype
    if rating:
        params["rating"] = rating
    if time:
        params["time"] = time
    if end_time:
        params["endtime"] = end_time
    if timerel:
        params["timerel"] = timerel
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/user/feedback/approved", token=token, params=params)



@mcp.tool()
async def list_platform_feedback(
    token: str,
    user_id: str = "",
    asset_id: str = "",
    feedback_status: str = "",
    action_subtype: str = "",
    rating: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """Admin: list all feedback on the platform (GET /iudx/v2/user/feedback/platform).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
        user_id: Query parameter `userId` (optional).
        asset_id: Query parameter `assetId` (optional).
        feedback_status: Query parameter `feedbackStatus` (optional).
        action_subtype: Query parameter `actionSubtype` (optional).
        rating: Query parameter `rating` (optional).
        time: Query parameter `time` (optional).
        end_time: Query parameter `endtime` (optional).
        timerel: Query parameter `timerel` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if user_id:
        params["userId"] = user_id
    if asset_id:
        params["assetId"] = asset_id
    if feedback_status:
        params["feedbackStatus"] = feedback_status
    if action_subtype:
        params["actionSubtype"] = action_subtype
    if rating:
        params["rating"] = rating
    if time:
        params["time"] = time
    if end_time:
        params["endtime"] = end_time
    if timerel:
        params["timerel"] = timerel
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/user/feedback/platform", token=token, params=params)



@mcp.tool()
async def list_my_feedback(
    token: str,
    asset_id: str = "",
    feedback_status: str = "",
    action_subtype: str = "",
    rating: str = "",
    time: str = "",
    end_time: str = "",
    timerel: str = "",
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List the authenticated user's feedback (GET /iudx/v2/user/feedback/user).

    Args:
        token: Bearer JWT.
        asset_id: Query parameter `assetId` (optional).
        feedback_status: Query parameter `feedbackStatus` (optional).
        action_subtype: Query parameter `actionSubtype` (optional).
        rating: Query parameter `rating` (optional).
        time: Query parameter `time` (optional).
        end_time: Query parameter `endtime` (optional).
        timerel: Query parameter `timerel` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if asset_id:
        params["assetId"] = asset_id
    if feedback_status:
        params["feedbackStatus"] = feedback_status
    if action_subtype:
        params["actionSubtype"] = action_subtype
    if rating:
        params["rating"] = rating
    if time:
        params["time"] = time
    if end_time:
        params["endtime"] = end_time
    if timerel:
        params["timerel"] = timerel
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/user/feedback/user", token=token, params=params)



@mcp.tool()
async def moderate_user_feedback(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Admin: approve / reject a feedback entry (PUT /iudx/v2/user/feedback/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "approved", "comment": "..."}'
        token: Bearer JWT (cos_admin).
    """
    return await _put(f"/iudx/v2/user/feedback/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def create_provider_feedback(
    body_json: str,
    token: str,
) -> dict:
    """Create provider feedback / FAQ / info for an asset (POST /iudx/v2/provider/feedback).

    Args:
        body_json: JSON string, e.g. '{"assetId": "<uuid>", "type": "FAQ", "data": [{"question": "...", "answer": "..."}]}'
                   type: FAQ | FEEDBACK | INFO | DATA_DESCRIPTION | SUGGESTION; data replaces the full list
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/provider/feedback", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_provider_feedback(
    body_json: str,
    token: str,
) -> dict:
    """Replace provider feedback entries for an asset+type (PUT /iudx/v2/provider/feedback).

    Args:
        body_json: JSON string, e.g. '{"assetId": "<uuid>", "type": "FAQ", "data": [{"question": "...", "answer": "..."}]}'
                   type: FAQ | FEEDBACK | INFO | DATA_DESCRIPTION | SUGGESTION; data replaces the full list
        token: Bearer JWT.
    """
    return await _put("/iudx/v2/provider/feedback", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_provider_feedback(
    token: str,
    asset_id: str = "",
    type: str = "",
    page: int = 0,
    size: int = 0,
) -> dict:
    """List provider feedback for an asset (GET /iudx/v2/provider/feedback).

    Args:
        token: Bearer JWT.
        asset_id: Query parameter `assetId` (optional).
        type: Query parameter `type` (optional).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
    """
    params: dict = {}
    if asset_id:
        params["assetId"] = asset_id
    if type:
        params["type"] = type
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    return await _get("/iudx/v2/provider/feedback", token=token, params=params)



@mcp.tool()
async def delete_provider_feedback(
    asset_id: str,
    type: str,
    token: str,
) -> dict:
    """Delete provider feedback for an asset+type (DELETE /iudx/v2/provider/feedback).

    Args:
        asset_id: Query parameter `assetId` (required).
        type: Query parameter `type` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["assetId"] = asset_id
    params["type"] = type
    return await _delete("/iudx/v2/provider/feedback", token=token, params=params)



@mcp.tool()
async def verify_kyc(
    body_json: str,
    token: str,
) -> dict:
    """Verify KYC with an authorisation code (POST /iudx/v2/auth/kyc/verify).

    Args:
        body_json: JSON string, e.g. '{"auth_code": "...", "code_verifier": "..."}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/kyc/verify", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def confirm_kyc(
    id: str,
    token: str,
) -> dict:
    """Confirm a KYC verification by ID (GET /iudx/v2/auth/kyc/confirm/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/kyc/confirm/{id}", token=token)



@mcp.tool()
async def revoke_kyc(token: str) -> dict:
    """Revoke the authenticated user's KYC (POST /iudx/v2/auth/kyc/revoke).

    Args:
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/kyc/revoke", token=token)



@mcp.tool()
async def list_my_org_creation_requests(token: str) -> dict:
    """List your own organisation creation requests (GET /iudx/v2/auth/user/organisations/requests).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/organisations/requests", token=token)



@mcp.tool()
async def delete_my_org_creation_request(
    id: str,
    token: str,
) -> dict:
    """Delete one of your own organisation creation requests (DELETE /iudx/v2/auth/user/organisations/requests/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/user/organisations/requests/{id}", token=token)



@mcp.tool()
async def list_my_org_join_requests(token: str) -> dict:
    """List your own organisation join requests (GET /iudx/v2/auth/user/organisations/join_requests).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/organisations/join_requests", token=token)



@mcp.tool()
async def delete_my_org_join_request(
    id: str,
    token: str,
) -> dict:
    """Delete one of your own organisation join requests (DELETE /iudx/v2/auth/user/organisations/join_requests/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/user/organisations/join_requests/{id}", token=token)



@mcp.tool()
async def submit_org_join_request(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Request to join an organisation (POST /iudx/v2/auth/organisations/{id}/join_requests).

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"job_title": "...", "emp_id": "...", "official_email": "..."}'
        token: Bearer JWT.
    """
    return await _post(f"/iudx/v2/auth/organisations/{id}/join_requests", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_org_join_request_status(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Update the status of an organisation join request (PATCH /iudx/v2/auth/organisation/join-request/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "granted"}' (granted | rejected)
        token: Bearer JWT.
    """
    return await _patch(f"/iudx/v2/auth/organisation/join-request/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_organisation(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Update an organisation (PUT /iudx/v2/auth/organisations/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"name": "...", "logo_path": "...", "entity_type": "...", "org_sector": "...",
                   "website_link": "...", "address": "...", "certificate_path": "...", "pancard_path": "...", "relevant_doc_path": "..."}'
        token: Bearer JWT.
    """
    return await _put(f"/iudx/v2/auth/organisations/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def delete_organisation(
    id: str,
    token: str,
) -> dict:
    """Delete an organisation (DELETE /iudx/v2/auth/organisations/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT (cos_admin).
    """
    return await _delete(f"/iudx/v2/auth/organisations/{id}", token=token)



@mcp.tool()
async def get_org_user(
    id: str,
    user_id: str,
    token: str,
) -> dict:
    """Fetch a user within an organisation (GET /iudx/v2/auth/organisations/{id}/users/{user_id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        user_id: Path parameter `user_id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/auth/organisations/{id}/users/{user_id}", token=token)



@mcp.tool()
async def update_org_user_role(
    id: str,
    user_id: str,
    body_json: str,
    token: str,
) -> dict:
    """Change a user's role within an organisation (PUT /iudx/v2/auth/organisations/{id}/users/{user_id}).

    Requires org_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        user_id: Path parameter `user_id` (UUID unless noted).
        body_json: JSON string, e.g. '{"role": "..."}'
        token: Bearer JWT (org_admin).
    """
    return await _put(f"/iudx/v2/auth/organisations/{id}/users/{user_id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def remove_org_user(
    id: str,
    user_id: str,
    token: str,
) -> dict:
    """Remove a user from an organisation (DELETE /iudx/v2/auth/organisations/{id}/users/{user_id}).

    Requires org_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        user_id: Path parameter `user_id` (UUID unless noted).
        token: Bearer JWT (org_admin).
    """
    return await _delete(f"/iudx/v2/auth/organisations/{id}/users/{user_id}", token=token)



@mcp.tool()
async def list_org_provider_requests(token: str) -> dict:
    """List organisation provider requests (GET /iudx/v2/auth/organization/user/provider_requests).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/organization/user/provider_requests", token=token)



@mcp.tool()
async def delete_org_provider_request(
    id: str,
    token: str,
) -> dict:
    """Delete an organisation provider request (DELETE /iudx/v2/auth/organization/user/provider-requests/{id}).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/auth/organization/user/provider-requests/{id}", token=token)



@mcp.tool()
async def create_org_provider_role_request(token: str) -> dict:
    """Request the provider role within your organisation (POST /iudx/v2/auth/organization/user/provider_role/requests).

    Args:
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/organization/user/provider_role/requests", token=token)



@mcp.tool()
async def list_org_provider_role_requests(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
    status: str = "",
) -> dict:
    """List organisation provider-role requests (GET /iudx/v2/auth/organization/user/provider_role/requests).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
        status: Query parameter `status` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    if status:
        params["status"] = status
    return await _get("/iudx/v2/auth/organization/user/provider_role/requests", token=token, params=params)



@mcp.tool()
async def update_org_provider_role_request(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Grant or reject a provider-role request (PUT /iudx/v2/auth/organization/user/provider_role/requests/{id}).

    Requires org_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "granted"}' (granted | rejected)
        token: Bearer JWT (org_admin).
    """
    return await _put(f"/iudx/v2/auth/organization/user/provider_role/requests/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def add_org_provider(
    body_json: str,
    token: str,
) -> dict:
    """Make a user a provider in an organisation (POST /iudx/v2/auth/organization/user/provider).

    Requires org_admin role.

    Args:
        body_json: JSON string, e.g. '{"user_id": "<uuid>", "organization_id": "<uuid>", "provider_type": "..."}'
        token: Bearer JWT (org_admin).
    """
    return await _post("/iudx/v2/auth/organization/user/provider", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def download_org_creation_requests_report(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
    status: str = "",
) -> dict:
    """Download organisation creation requests report as CSV (GET /iudx/v2/auth/organisations/requests/report).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
        status: Query parameter `status` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    if status:
        params["status"] = status
    return await _get_text("/iudx/v2/auth/organisations/requests/report", token=token, params=params)



@mcp.tool()
async def download_organisations_report(token: str) -> dict:
    """Download organisations report as CSV (GET /iudx/v2/auth/organisations/report).

    Args:
        token: Bearer JWT.
    """
    return await _get_text("/iudx/v2/auth/organisations/report", token=token)



@mcp.tool()
async def download_org_join_requests_report(
    id: str,
    token: str,
) -> dict:
    """Download an organisation's join requests report as CSV (GET /iudx/v2/auth/organisations/{id}/join_requests/report).

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _get_text(f"/iudx/v2/auth/organisations/{id}/join_requests/report", token=token)



@mcp.tool()
async def download_provider_role_requests_report(token: str) -> dict:
    """Download provider-role requests report as CSV (GET /iudx/v2/auth/organization/user/provider_role/requests/report).

    Args:
        token: Bearer JWT.
    """
    return await _get_text("/iudx/v2/auth/organization/user/provider_role/requests/report", token=token)



@mcp.tool()
async def create_platform_provider_request(token: str) -> dict:
    """Request the platform provider role (POST /iudx/v2/auth/user/platform/provider-requests).

    Args:
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/user/platform/provider-requests", token=token)



@mcp.tool()
async def get_my_platform_provider_request(token: str) -> dict:
    """Fetch your platform provider request (GET /iudx/v2/auth/user/platform/provider-requests).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/platform/provider-requests", token=token)



@mcp.tool()
async def delete_my_platform_provider_request(token: str) -> dict:
    """Delete your platform provider request (DELETE /iudx/v2/auth/user/platform/provider-requests).

    Args:
        token: Bearer JWT.
    """
    return await _delete("/iudx/v2/auth/user/platform/provider-requests", token=token)



@mcp.tool()
async def admin_list_platform_provider_requests(
    token: str,
    page: int = 0,
    size: int = 0,
    status: str = "",
    user_id: str = "",
    sort: str = "",
) -> dict:
    """Admin: list platform provider requests (GET /iudx/v2/auth/admin/platform/provider-requests).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        status: Query parameter `status` (optional).
        user_id: Query parameter `userId` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if status:
        params["status"] = status
    if user_id:
        params["userId"] = user_id
    if sort:
        params["sort"] = sort
    return await _get("/iudx/v2/auth/admin/platform/provider-requests", token=token, params=params)



@mcp.tool()
async def admin_update_platform_provider_request(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Admin: grant / reject a platform provider request (PATCH /iudx/v2/auth/admin/platform/provider-requests/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "granted"}' (granted | rejected)
        token: Bearer JWT (cos_admin).
    """
    return await _patch(f"/iudx/v2/auth/admin/platform/provider-requests/{id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def share_asset(
    body_json: str,
    token: str,
) -> dict:
    """Share an asset with users / organisations (POST /iudx/v2/cat/assets/share).

    Args:
        body_json: JSON string, e.g. '{"itemId": "<uuid>", "shareType": "...", "ids": ["<uuid>"]}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/cat/assets/share", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def unshare_asset(
    body_json: str,
    token: str,
) -> dict:
    """Revoke sharing of an asset (DELETE /iudx/v2/cat/assets/share).

    Args:
        body_json: JSON string, e.g. '{"itemId": "<uuid>", "shareType": "...", "ids": ["<uuid>"]}'
        token: Bearer JWT.
    """
    return await _delete("/iudx/v2/cat/assets/share", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_asset_shares(
    item_id: str,
    token: str,
) -> dict:
    """List who an asset is shared with (GET /iudx/v2/cat/assets/share).

    Args:
        item_id: Query parameter `itemId` (required).
        token: Bearer JWT.
    """
    params: dict = {}
    params["itemId"] = item_id
    return await _get("/iudx/v2/cat/assets/share", token=token, params=params)



@mcp.tool()
async def list_assets_shared_with_me(token: str) -> dict:
    """List assets shared with the authenticated user (GET /iudx/v2/cat/assets/shared-with-me).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/cat/assets/shared-with-me", token=token)



@mcp.tool()
async def request_custom_role(
    body_json: str,
    token: str,
) -> dict:
    """Request a custom role / scope for a user (POST /iudx/v2/auth/user/custom/role).

    Args:
        body_json: JSON string, e.g. '{"user_id": "<uuid>", "scope": "..."}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/user/custom/role", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_custom_roles(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
    role: str = "",
    user_id: str = "",
) -> dict:
    """List custom role requests (GET /iudx/v2/auth/user/custom/role).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
        role: Query parameter `role` (optional).
        user_id: Query parameter `userId` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    if role:
        params["role"] = role
    if user_id:
        params["userId"] = user_id
    return await _get("/iudx/v2/auth/user/custom/role", token=token, params=params)



@mcp.tool()
async def delete_custom_role(
    body_json: str,
    token: str,
) -> dict:
    """Delete a custom role grant (DELETE /iudx/v2/auth/user/custom/role).

    Args:
        body_json: JSON string, e.g. '{"requestId": "<uuid>", "userId": "<uuid>", "scope": "..."}'
        token: Bearer JWT.
    """
    return await _delete("/iudx/v2/auth/user/custom/role", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_custom_role_requesters(
    token: str,
    page: int = 0,
    size: int = 0,
    sort: str = "",
) -> dict:
    """List custom-role requesters (GET /auth/v2/custom-role/requester).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        sort: Query parameter `sort` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if sort:
        params["sort"] = sort
    return await _get("/auth/v2/custom-role/requester", token=token, params=params)



@mcp.tool()
async def change_my_password(
    body_json: str,
    token: str,
) -> dict:
    """Change the authenticated user's password (PUT /iudx/v2/auth/user/password).

    Args:
        body_json: JSON string, e.g. '{"new_password": "..."}'
        token: Bearer JWT.
    """
    return await _put("/iudx/v2/auth/user/password", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def list_users_basic(
    token: str,
    page: int = 0,
    size: int = 0,
    search_term: str = "",
) -> dict:
    """List users (basic details) (GET /iudx/v2/auth/user/basic).

    Args:
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
        search_term: Query parameter `search_term` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    if search_term:
        params["search_term"] = search_term
    return await _get("/iudx/v2/auth/user/basic", token=token, params=params)



@mcp.tool()
async def get_user_basic_by_identifier(
    token: str,
    user_id: str = "",
    email: str = "",
) -> dict:
    """Look up a user (basic details) by user ID or email (GET /iudx/v2/auth/user/basic/by-identifier).

    Args:
        token: Bearer JWT.
        user_id: Query parameter `userId` (optional).
        email: Query parameter `email` (optional).
    """
    params: dict = {}
    if user_id:
        params["userId"] = user_id
    if email:
        params["email"] = email
    return await _get("/iudx/v2/auth/user/basic/by-identifier", token=token, params=params)



@mcp.tool()
async def update_my_account_status(
    body_json: str,
    token: str,
) -> dict:
    """Activate / deactivate your own account (POST /iudx/v2/auth/user/update).

    Args:
        body_json: JSON string, e.g. '{"status": "deactivate"}' (activate | deactivate)
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/user/update", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def admin_update_user_account_status(
    id: str,
    body_json: str,
    token: str,
) -> dict:
    """Admin: activate / deactivate a user account (POST /iudx/v2/auth/admin/{id}/update).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        body_json: JSON string, e.g. '{"status": "deactivate"}' (activate | deactivate)
        token: Bearer JWT (cos_admin).
    """
    return await _post(f"/iudx/v2/auth/admin/{id}/update", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def delete_my_account(token: str) -> dict:
    """Delete the authenticated user's account (DELETE /iudx/v2/auth/user/delete).

    Args:
        token: Bearer JWT.
    """
    return await _delete("/iudx/v2/auth/user/delete", token=token)



@mcp.tool()
async def create_my_description(
    body_json: str,
    token: str,
) -> dict:
    """Create the user's profile description (POST /iudx/v2/auth/user/description/info).

    Args:
        body_json: JSON string, e.g. '{"about": "...", "experience": [], "education": [], "projects": [],
                   "publications": [], "skills": []}'
        token: Bearer JWT.
    """
    return await _post("/iudx/v2/auth/user/description/info", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def update_my_description(
    body_json: str,
    token: str,
) -> dict:
    """Update the user's profile description (PATCH /iudx/v2/auth/user/description/info).

    Args:
        body_json: JSON string, e.g. '{"about": "...", "experience": [], "education": [], "projects": [],
                   "publications": [], "skills": []}'
        token: Bearer JWT.
    """
    return await _patch("/iudx/v2/auth/user/description/info", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def get_my_description(token: str) -> dict:
    """Fetch the user's profile description (GET /iudx/v2/auth/user/description/info).

    Args:
        token: Bearer JWT.
    """
    return await _get("/iudx/v2/auth/user/description/info", token=token)



@mcp.tool()
async def list_acl_servers(token: str) -> dict:
    """List ACL servers (GET /iudx/v2/acl_servers).

    Requires cos_admin role.

    Args:
        token: Bearer JWT (cos_admin).
    """
    return await _get("/iudx/v2/acl_servers", token=token)



@mcp.tool()
async def create_acl_server(
    body_json: str,
    token: str,
) -> dict:
    """Register an ACL server (POST /iudx/v2/acl_servers).

    Requires cos_admin role.

    Args:
        body_json: JSON string, e.g. '{"name": "DX ACL APD Server", "url": "acl-apd.iudx.io", "visibility": "PUBLIC"}'
        token: Bearer JWT (cos_admin).
    """
    return await _post("/iudx/v2/acl_servers", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def get_acl_server(
    id: str,
    token: str,
) -> dict:
    """Fetch an ACL server by ID (GET /iudx/v2/acl_servers/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT (cos_admin).
    """
    return await _get(f"/iudx/v2/acl_servers/{id}", token=token)



@mcp.tool()
async def delete_acl_server(
    id: str,
    token: str,
) -> dict:
    """Delete an ACL server by ID (DELETE /iudx/v2/acl_servers/{id}).

    Requires cos_admin role.

    Args:
        id: Path parameter `id` (UUID unless noted).
        token: Bearer JWT (cos_admin).
    """
    return await _delete(f"/iudx/v2/acl_servers/{id}", token=token)



@mcp.tool()
async def list_request_conversations(
    request_id: str,
    token: str,
    page: int = 0,
    size: int = 0,
) -> dict:
    """List conversation messages on a request (GET /iudx/v2/requests/{request_id}/conversations).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        token: Bearer JWT.
        page: Query parameter `page` (optional).
        size: Query parameter `size` (optional).
    """
    params: dict = {}
    if page:
        params["page"] = page
    if size:
        params["size"] = size
    return await _get(f"/iudx/v2/requests/{request_id}/conversations", token=token, params=params)



@mcp.tool()
async def post_request_message(
    request_id: str,
    body_json: str,
    token: str,
) -> dict:
    """Post a message on a request conversation (POST /iudx/v2/requests/{request_id}/conversations).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        body_json: JSON string, e.g. '{"parent_msg_id": null, "sender_role": "...", "message_type": "...", "request_type": "...",
                   "content": "...", "is_internal": false, "metadata": {}}'
        token: Bearer JWT.
    """
    return await _post(f"/iudx/v2/requests/{request_id}/conversations", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def get_request_message(
    request_id: str,
    msg_id: str,
    token: str,
) -> dict:
    """Fetch a conversation message (GET /iudx/v2/requests/{request_id}/conversations/{msg_id}).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        msg_id: Path parameter `msg_id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _get(f"/iudx/v2/requests/{request_id}/conversations/{msg_id}", token=token)



@mcp.tool()
async def update_request_message(
    request_id: str,
    msg_id: str,
    body_json: str,
    token: str,
) -> dict:
    """Edit a conversation message (PUT /iudx/v2/requests/{request_id}/conversations/{msg_id}).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        msg_id: Path parameter `msg_id` (UUID unless noted).
        body_json: JSON string, e.g. '{"content": "...", "metadata": {}, "is_internal": false}'
        token: Bearer JWT.
    """
    return await _put(f"/iudx/v2/requests/{request_id}/conversations/{msg_id}", token=token, body=_parse(body_json, "body_json"))



@mcp.tool()
async def delete_request_message(
    request_id: str,
    msg_id: str,
    token: str,
) -> dict:
    """Delete a conversation message (DELETE /iudx/v2/requests/{request_id}/conversations/{msg_id}).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        msg_id: Path parameter `msg_id` (UUID unless noted).
        token: Bearer JWT.
    """
    return await _delete(f"/iudx/v2/requests/{request_id}/conversations/{msg_id}", token=token)



@mcp.tool()
async def reply_to_request_message(
    request_id: str,
    msg_id: str,
    body_json: str,
    token: str,
) -> dict:
    """Reply to a conversation message (POST /iudx/v2/requests/{request_id}/conversations/{msg_id}/reply).

    Args:
        request_id: Path parameter `request_id` (UUID unless noted).
        msg_id: Path parameter `msg_id` (UUID unless noted).
        body_json: JSON string, e.g. '{"sender_role": "...", "message_type": "...", "content": "...", "is_internal": false, "metadata": {}}'
        token: Bearer JWT.
    """
    return await _post(f"/iudx/v2/requests/{request_id}/conversations/{msg_id}/reply", token=token, body=_parse(body_json, "body_json"))


@mcp.tool()
async def get_token_with_client_credentials(
    client_id: str,
    client_secret: str,
    item_id: str = "",
) -> dict:
    """Issue a JWT using clientId/clientSecret headers (POST /iudx/v2/auth/token).

    Without item_id an identity token is returned; with item_id an access token
    scoped to that resource is returned. (To refresh using a Bearer token instead,
    use `get_token`.)

    Args:
        client_id:     Client UUID from `create_client_credentials`.
        client_secret: Client secret from `create_client_credentials`.
        item_id:       Optional item UUID to scope the access token to.
    """
    return await _post(
        "/iudx/v2/auth/token",
        body={"itemId": item_id} if item_id else None,
        extra_headers={"clientId": client_id, "clientSecret": client_secret},
    )
