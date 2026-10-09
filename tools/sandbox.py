from typing import Any
from ._app import (
    mcp,
    _sandbox_get,
    _sandbox_post,
    _sandbox_put,
    _sandbox_patch,
    _sandbox_delete,
)


# ===========================================================================
# Sandbox Connect API Tools
# ===========================================================================

# ---------------------------------------------------------------------------
# Bookings — lifecycle
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_sandbox_bookings(
    token: str,
    status: str = "",
    limit: int = 0,
    offset: int = 0,
) -> dict:
    """List CPU/GPU slot bookings for the current user (GET /v1/bookings).

    Booking lifecycle states: scheduled → ready → active → shutting_down →
    completed, with cancelled and expired as terminal states.
    notebookUrl is returned only for active bookings whose notebook resource
    has been applied.

    Args:
        token: Bearer JWT token.
        status: Comma-separated status filter — scheduled, ready, active,
                shutting_down, completed, cancelled, expired — or 'all' to
                disable filtering. Empty uses the server default.
        limit: Max rows to return (default 10, max 50; 0 = server default).
        offset: Pagination offset.
    """
    params: dict[str, Any] = {}
    if status:
        params["status"] = status
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    return await _sandbox_get("/v1/bookings", token=token, params=params or None)


@mcp.tool()
async def create_sandbox_booking(
    category: str,
    notebook_name: str,
    slot_date: str,
    slot_keys: str,
    token: str,
    file_url: str = "",
    git_url: str = "",
    git_access_token: str = "",
    git_token_secret_name: str = "",
) -> dict:
    """Create a CPU or GPU notebook slot booking (POST /v1/bookings).

    New bookings are inserted as 'scheduled'; the lifecycle service provisions
    the notebook at slot start and cleans up at slot end. Two limits apply per
    user and category: MaxActiveBookings (counts scheduled/ready/active/
    shutting_down) and MaxBookingsPerWeek (also counts completed). Cancelled
    bookings count toward neither; expired bookings do not count toward the
    weekly quota.

    Args:
        category: Booking category name (from list_sandbox_categories, e.g. CPU or GPU).
        notebook_name: Name for the notebook to provision.
        slot_date: Slot date in YYYY-MM-DD (IST).
        slot_keys: Comma-separated slot keys (from list_available_sandbox_slots).
        token: Bearer JWT token.
        file_url: Optional URL of a notebook file to preload.
        git_url: Optional git repository URL to clone into the notebook.
        git_access_token: Optional git access token for private repositories.
        git_token_secret_name: Optional name of an existing secret holding the git token.
    """
    body: dict[str, Any] = {
        "category": category,
        "notebookName": notebook_name,
        "slotDate": slot_date,
        "slotKeys": [k.strip() for k in slot_keys.split(",") if k.strip()],
    }
    if file_url:
        body["fileUrl"] = file_url
    if git_url:
        body["gitUrl"] = git_url
    if git_access_token:
        body["gitAccessToken"] = git_access_token
    if git_token_secret_name:
        body["gitTokenSecretName"] = git_token_secret_name
    return await _sandbox_post("/v1/bookings", token=token, body=body)


@mcp.tool()
async def cancel_sandbox_booking(booking_id: int, token: str) -> dict:
    """Cancel a 'scheduled' booking before resources are ready (PATCH /v1/bookings/{id}/cancel).

    Changes 'scheduled' to 'cancelled'. Does not operate on ready, active, or
    shutting_down bookings — use terminate_sandbox_booking for those states.

    Args:
        booking_id: Booking ID.
        token: Bearer JWT token.
    """
    return await _sandbox_patch(f"/v1/bookings/{booking_id}/cancel", token=token)


@mcp.tool()
async def extend_sandbox_booking(booking_id: int, token: str) -> dict:
    """Extend an 'active' booking by one contiguous slot (PATCH /v1/bookings/{id}/extend).

    Succeeds only if the next contiguous slot has capacity, the category's
    contiguous-slot limit is not reached, and the booking has not already been
    extended (one extension per booking). The booking stays 'active' with an
    updated slot end.

    Args:
        booking_id: Booking ID.
        token: Bearer JWT token.
    """
    return await _sandbox_patch(f"/v1/bookings/{booking_id}/extend", token=token)


@mcp.tool()
async def terminate_sandbox_booking(booking_id: int, token: str) -> dict:
    """End a 'ready', 'active', or 'shutting_down' booking early (PATCH /v1/bookings/{id}/terminate).

    Marks the booking 'completed', unlinks the notebook, and best-effort
    deletes the linked Notebook/PVC. Already-completed bookings return success
    unchanged. Use cancel or reset for 'scheduled' bookings.

    Args:
        booking_id: Booking ID.
        token: Bearer JWT token.
    """
    return await _sandbox_patch(f"/v1/bookings/{booking_id}/terminate", token=token)


@mcp.tool()
async def reset_sandbox_booking(booking_id: int, token: str) -> dict:
    """Reset a stuck 'scheduled' or 'ready' booking (PATCH /v1/bookings/{id}/reset).

    'scheduled' resets become 'cancelled' and unlink any notebook id.
    'ready' resets become 'expired', set cleanup timestamps, and best-effort
    delete the linked Notebook/PVC. Does not apply to active, shutting_down,
    completed, cancelled, or already expired bookings.

    Args:
        booking_id: Booking ID.
        token: Bearer JWT token.
    """
    return await _sandbox_patch(f"/v1/bookings/{booking_id}/reset", token=token)


# ---------------------------------------------------------------------------
# Bookings — notebook token sessions
# ---------------------------------------------------------------------------


@mcp.tool()
async def create_booking_notebook_token_session(booking_id: int, token: str) -> dict:
    """Create a notebook token session for a booking (POST /v1/bookings/{id}/notebook-token-session).

    Exchanges the caller access token for a notebook-specific delegated
    refresh token and stores it in a notebook-scoped Kubernetes Secret.
    Browser refresh tokens are never accepted or stored.

    Args:
        booking_id: Booking ID.
        token: Bearer JWT token.
    """
    return await _sandbox_post(
        f"/v1/bookings/{booking_id}/notebook-token-session", token=token
    )


@mcp.tool()
async def rotate_booking_notebook_token(
    booking_id: int, refresh_token: str, token: str
) -> dict:
    """Persist a rotated notebook refresh token for a booking (PUT /v1/bookings/{id}/notebook-token-session).

    Replaces the notebook refresh token after Keycloak rotation. Accepts only
    a delegated notebook-client access token belonging to the booking owner.

    Args:
        booking_id: Booking ID.
        refresh_token: The rotated refresh token to persist.
        token: Delegated notebook-client bearer access token of the booking owner.
    """
    return await _sandbox_put(
        f"/v1/bookings/{booking_id}/notebook-token-session",
        token=token,
        body={"refreshToken": refresh_token},
    )


# ---------------------------------------------------------------------------
# Categories & slot availability
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_sandbox_categories(token: str) -> dict:
    """List booking categories and their slot templates (GET /v1/categories).

    Returns configured CPU and GPU categories with limits (max active
    bookings, weekly quota, concurrent users), grace periods, and the slot
    templates available for booking. Browser categories (e.g. JupyterLite)
    have launchMode 'direct' and are not bookable.

    Args:
        token: Bearer JWT token.
    """
    return await _sandbox_get("/v1/categories", token=token)


@mcp.tool()
async def list_available_sandbox_slots(category: str, date: str, token: str) -> dict:
    """List slot-level availability for a category on a date (GET /v1/slots/available).

    Args:
        category: Category name (CPU or GPU).
        date: Date in YYYY-MM-DD (IST).
        token: Bearer JWT token.
    """
    return await _sandbox_get(
        "/v1/slots/available", token=token, params={"category": category, "date": date}
    )


@mcp.tool()
async def get_sandbox_slots_calendar(category: str, month: str, token: str) -> dict:
    """Get day-level availability totals for a category and month (GET /v1/slots/calendar).

    Args:
        category: Category name (CPU or GPU).
        month: Month in YYYY-MM.
        token: Bearer JWT token.
    """
    return await _sandbox_get(
        "/v1/slots/calendar", token=token, params={"category": category, "month": month}
    )


@mcp.tool()
async def list_sandbox_instance_types(token: str) -> dict:
    """List instance types for GPU-backed booking categories (GET /v1/notebook/instance-types).

    Returns instance types with display metadata: display name, GPU memory,
    session duration, and description.

    Args:
        token: Bearer JWT token.
    """
    return await _sandbox_get("/v1/notebook/instance-types", token=token)


# ---------------------------------------------------------------------------
# Notebooks — direct management (available when API_BOOKINGS_ENABLED=false)
# ---------------------------------------------------------------------------


@mcp.tool()
async def create_sandbox_notebook(
    name: str,
    notebook_type: str,
    token: str,
    image_name: str = "",
    instance_type: str = "",
    file_url: str = "",
    git_url: str = "",
    git_access_token: str = "",
    git_token_secret_name: str = "",
) -> dict:
    """Create a CPU or GPU notebook directly, without a booking (POST /v1/notebook/create).

    Available when the deployment runs with API_BOOKINGS_ENABLED=false.
    The notebook stays live until stopped or deleted.

    Args:
        name: Notebook name (4–50 characters).
        notebook_type: Notebook type, e.g. 'cpu' or 'gpu'.
        token: Bearer JWT token.
        image_name: Optional container image for the notebook.
        instance_type: Optional instance type (see list_sandbox_instance_types).
        file_url: Optional URL of a notebook file to preload.
        git_url: Optional git repository URL to clone into the notebook.
        git_access_token: Optional git access token for private repositories.
        git_token_secret_name: Optional name of an existing secret holding the git token.
    """
    body: dict[str, Any] = {"name": name, "type": notebook_type}
    if image_name:
        body["imageName"] = image_name
    if instance_type:
        body["instanceType"] = instance_type
    if file_url:
        body["fileUrl"] = file_url
    if git_url:
        body["gitUrl"] = git_url
    if git_access_token:
        body["gitAccessToken"] = git_access_token
    if git_token_secret_name:
        body["gitTokenSecretName"] = git_token_secret_name
    return await _sandbox_post("/v1/notebook/create", token=token, body=body)


@mcp.tool()
async def list_sandbox_notebooks(
    token: str,
    limit: int = 0,
    offset: int = 0,
    order: str = "",
    date_filter: str = "",
) -> dict:
    """List all notebooks for the user (GET /v1/notebook/list).

    Args:
        token: Bearer JWT token.
        limit: Maximum number of notebooks to return (max 50; 0 = server default).
        offset: Offset for pagination.
        order: Sort order — 'asc' or 'desc'.
        date_filter: Date filter as a JSON array of two date strings, e.g.
                     '["2026-07-01", "2026-07-08"]'.
    """
    params: dict[str, Any] = {}
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if order:
        params["order"] = order
    if date_filter:
        params["filter"] = date_filter
    return await _sandbox_get("/v1/notebook/list", token=token, params=params or None)


@mcp.tool()
async def get_sandbox_notebook_status(notebook_name: str, token: str) -> dict:
    """Get the status of a notebook (GET /v1/notebook/status/{notebook_name}).

    Status is one of: opening, running, stopped, failed, orphaned. The
    response includes resource requests/limits, image, PVC, provisioning
    events, and the linked booking when one exists.

    Args:
        notebook_name: Notebook name.
        token: Bearer JWT token.
    """
    return await _sandbox_get(f"/v1/notebook/status/{notebook_name}", token=token)


@mcp.tool()
async def check_sandbox_notebook_exists(notebook_name: str, token: str) -> dict:
    """Check if a notebook with the given name exists (GET /v1/notebook/check-exists/{notebook_name}).

    Args:
        notebook_name: Notebook name.
        token: Bearer JWT token.
    """
    return await _sandbox_get(f"/v1/notebook/check-exists/{notebook_name}", token=token)


@mcp.tool()
async def start_sandbox_notebook(name: str, token: str) -> dict:
    """Start a directly managed stopped notebook (PATCH /v1/notebook/start).

    Removes the Kubeflow stopped annotation. Available when API_BOOKINGS_ENABLED=false.

    Args:
        name: Notebook name (4–50 characters).
        token: Bearer JWT token.
    """
    return await _sandbox_patch("/v1/notebook/start", token=token, body={"name": name})


@mcp.tool()
async def stop_sandbox_notebook(name: str, token: str) -> dict:
    """Stop a directly managed notebook (PATCH /v1/notebook/stop).

    Adds the Kubeflow stopped annotation. Available when API_BOOKINGS_ENABLED=false.

    Args:
        name: Notebook name (4–50 characters).
        token: Bearer JWT token.
    """
    return await _sandbox_patch("/v1/notebook/stop", token=token, body={"name": name})


@mcp.tool()
async def delete_sandbox_notebook(name: str, token: str) -> dict:
    """Delete a directly managed notebook and its PVC (DELETE /v1/notebook/delete).

    Available when API_BOOKINGS_ENABLED=false. This permanently removes the
    notebook and its persistent storage.

    Args:
        name: Notebook name (4–50 characters).
        token: Bearer JWT token.
    """
    return await _sandbox_delete("/v1/notebook/delete", token=token, body={"name": name})


@mcp.tool()
async def create_notebook_token_session(notebook_name: str, token: str) -> dict:
    """Create a token session for a direct notebook (POST /v1/notebook/{notebook_name}/notebook-token-session).

    Exchanges the caller access token for a notebook-specific delegated
    refresh token stored in a notebook-scoped Kubernetes Secret. Available
    for direct notebooks when API_BOOKINGS_ENABLED=false.

    Args:
        notebook_name: Notebook name.
        token: Bearer JWT token.
    """
    return await _sandbox_post(
        f"/v1/notebook/{notebook_name}/notebook-token-session", token=token
    )


@mcp.tool()
async def rotate_notebook_token(
    notebook_name: str, refresh_token: str, token: str
) -> dict:
    """Persist a rotated refresh token for a direct notebook (PUT /v1/notebook/{notebook_name}/notebook-token-session).

    Replaces the direct notebook refresh token after Keycloak rotation.
    Accepts only a delegated notebook-client access token belonging to the
    notebook owner. Available when API_BOOKINGS_ENABLED=false.

    Args:
        notebook_name: Notebook name.
        refresh_token: The rotated refresh token to persist.
        token: Delegated notebook-client bearer access token of the notebook owner.
    """
    return await _sandbox_put(
        f"/v1/notebook/{notebook_name}/notebook-token-session",
        token=token,
        body={"refreshToken": refresh_token},
    )


# ---------------------------------------------------------------------------
# JupyterLite & profile
# ---------------------------------------------------------------------------


@mcp.tool()
async def create_jupyterlite_session(token: str) -> dict:
    """Create a JupyterLite launch session (POST /v1/jupyterlite/session).

    Validates the bearer token and sets an HttpOnly cookie so browser
    navigations to JupyterLite can authenticate without putting the token in
    the URL. Returns the launch URL.

    Args:
        token: Bearer JWT token.
    """
    return await _sandbox_post("/v1/jupyterlite/session", token=token)


@mcp.tool()
async def create_kubeflow_profile(token: str) -> dict:
    """Create a Kubeflow Profile CRD for the current user (POST /v1/profile/create).

    Required before notebooks can be provisioned in the user's namespace.

    Args:
        token: Bearer JWT token.
    """
    return await _sandbox_post("/v1/profile/create", token=token)
