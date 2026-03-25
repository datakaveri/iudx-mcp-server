from ._app import mcp


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


# ---------------------------------------------------------------------------
# Resource Server prompts
# ---------------------------------------------------------------------------

@mcp.prompt()
def query_resource_data(
    resource_id: str,
    timerel: str = "before",
    time_at: str = "",
) -> str:
    """Guide the user through querying time-series or spatial data from the RS.

    Args:
        resource_id: UUID of the IUDX resource to query.
        timerel:     Time relationship hint — between, before, or after.
        time_at:     ISO-8601 timestamp hint (defaults to now if omitted).
    """
    time_hint = f" Use timeAt='{time_at}'" if time_at else " Use the current UTC time as timeAt."
    return (
        f"Help the user query data for IUDX resource '{resource_id}' from the Resource Server.\n\n"
        "Steps:\n"
        "1. If the user doesn't have a token, advise them to call get_token with their credentials first.\n"
        f"2. Call rs_get_temporal_entities with resource_id='{resource_id}', timerel='{timerel}'.{time_hint}\n"
        "3. If the user needs spatial filtering (e.g. near a location), switch to rs_post_temporal_query "
        "and include a geoQ block.\n"
        "4. If the user wants the latest snapshot without time filtering, use rs_get_latest_entity_data instead.\n"
        "5. Summarise the returned records: count, time range, and key measured properties.\n"
        "6. Ask whether the user wants to download the full dataset as CSV using rs_download_entity_data."
    )


@mcp.prompt()
def download_resource_data(
    resource_id: str,
    start_time: str = "",
    end_time: str = "",
) -> str:
    """Guide the user through downloading resource data as CSV.

    Args:
        resource_id: UUID of the IUDX resource.
        start_time:  Optional ISO-8601 start for filtering (e.g. "2024-01-01T00:00:00Z").
        end_time:    Optional ISO-8601 end for filtering.
    """
    if start_time and end_time:
        filter_note = (
            f" Apply a temporal filter: betweenTemporal from '{start_time}' to '{end_time}'."
        )
        tool = "rs_download_entity_data_post"
        extra = (
            f" Build the search_criteria_json with a betweenTemporal criterion on "
            f"observationDateTime between '{start_time}' and '{end_time}'."
        )
    else:
        filter_note = ""
        tool = "rs_download_entity_data"
        extra = ""
    return (
        f"Download data for IUDX resource '{resource_id}' as CSV.{filter_note}\n\n"
        "Steps:\n"
        "1. Ensure the user has a valid token (call get_token if needed).\n"
        f"2. Call {tool} with resource_id='{resource_id}'.{extra}\n"
        "3. Confirm the number of rows in the returned CSV and show the column headers.\n"
        "4. Advise the user to save the CSV to a file for further analysis."
    )


@mcp.prompt()
def ingest_resource_data(resource_id: str) -> str:
    """Guide a data provider through ingesting data into an IUDX resource.

    Args:
        resource_id: UUID of the IUDX resource to publish data to.
    """
    return (
        f"Help the user ingest data into IUDX resource '{resource_id}'.\n\n"
        "Steps:\n"
        "1. Confirm the user has a Bearer token with data-ingestion privileges. "
        "If not, call get_token first.\n"
        "2. Ask the user for the data payload (JSON array of observations).\n"
        "3. Verify each observation has the required 'observationDateTime' field "
        "in ISO-8601 format with timezone offset.\n"
        "4. Choose the ingestion endpoint:\n"
        "   - rs_ingest_entities_publish: standard publish (resource_id in path, not body).\n"
        "   - rs_ingest_entities_on_seek: if the data stream supports seeking.\n"
        "   - rs_ingest_entities: if multiple resources are being published in one call "
        "(embed resource UUID in each record's 'entities' field).\n"
        f"5. Call the chosen tool with resource_id='{resource_id}'.\n"
        "6. Confirm success and report how many records were ingested."
    )


# ---------------------------------------------------------------------------
# Resource Server Proxy (RSP) prompts
# ---------------------------------------------------------------------------

@mcp.prompt()
def rsp_query_spatial_data(
    resource_id: str,
    georel: str = "within",
    geometry: str = "Polygon",
    coordinates: str = "",
) -> str:
    """Guide the user through a spatial query via the Resource Server Proxy (RSP).

    Args:
        resource_id:  IUDX resource UUID to query.
        georel:       Geo-relationship: within, near, intersects, contains, etc.
        geometry:     Geometry type: Polygon, Point, LineString, etc.
        coordinates:  GeoJSON coordinates string for the spatial filter.
    """
    geo_hint = (
        f" Apply a spatial filter: georel='{georel}', geometry='{geometry}'"
        + (f", coordinates='{coordinates}'" if coordinates else " (ask the user for coordinates).")
    )
    return (
        f"Help the user query spatial data for IUDX resource '{resource_id}' via the RSP.\n\n"
        "Steps:\n"
        "1. If the user doesn't have a token and the resource is SECURE, advise them to call "
        "get_token first.\n"
        f"2. Call rsp_get_entities_v2 with resource_id='{resource_id}'.{geo_hint}\n"
        "3. If the query body is complex (large polygon, multiple entity IDs, attribute filter), "
        "switch to rsp_post_entities_query_v2 instead.\n"
        "4. Summarise the returned entities: count, key attributes (e.g. temperature, AQI), "
        "and their geographic distribution.\n"
        "5. Ask if the user wants to refine the search (change radius, add attribute filter with q=, "
        "or project specific fields with pick=)."
    )


@mcp.prompt()
def rsp_query_temporal_data(
    resource_id: str,
    timerel: str = "between",
    time_at: str = "",
    end_time_at: str = "",
) -> str:
    """Guide the user through a temporal query via the Resource Server Proxy (RSP).

    Args:
        resource_id: IUDX resource UUID to query.
        timerel:     Temporal relationship: between, before, or after.
        time_at:     ISO-8601 anchor timestamp (start of range for 'between').
        end_time_at: ISO-8601 end timestamp. Required when timerel='between'.
    """
    time_hint = ""
    if time_at:
        time_hint = f" Use timeAt='{time_at}'"
        if end_time_at:
            time_hint += f" and endTimeAt='{end_time_at}'"
        time_hint += "."
    else:
        time_hint = " Ask the user for the time range (start and end ISO-8601 timestamps)."

    return (
        f"Help the user query time-series data for IUDX resource '{resource_id}' via the RSP.\n\n"
        "Steps:\n"
        "1. If the user doesn't have a token and the resource is SECURE, advise them to call "
        "get_token first.\n"
        f"2. Call rsp_get_temporal_entities_v2 with resource_id='{resource_id}', "
        f"timerel='{timerel}'.{time_hint}\n"
        "3. If the user also needs spatial filtering (e.g. near a city), combine both filters "
        "using rsp_post_temporal_query_v2 with a temporalQ + geoQ body.\n"
        "4. Summarise the returned records: count, time span covered, and key measured properties.\n"
        "5. Ask if the user wants to narrow the time window, add an attribute filter (q=), "
        "or change the sort order (orderBy=observationDateTime:asc)."
    )
