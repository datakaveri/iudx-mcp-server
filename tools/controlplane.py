from typing import Any
from ._app import mcp, _get, _post, _put, _delete, _parse


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
