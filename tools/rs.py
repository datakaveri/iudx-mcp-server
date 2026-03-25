from typing import Any
from ._app import mcp, ES_INDEX_PREFIX, _rs_get, _rs_post, _rs_get_text, _rs_post_text, _parse


# ---------------------------------------------------------------------------
# Resource Server (RS) — Data Query & Ingestion
# ---------------------------------------------------------------------------

@mcp.tool()
async def rs_get_temporal_entities(
    resource_id: str,
    timerel: str,
    time_at: str,
    token: str,
    end_time_at: str = "",
    time_property: str = "observationDateTime",
    limit: int = 100,
    offset: int = 0,
    last_n: int = 0,
    count: bool = False,
    q: str = "",
    omit: str = "",
    order_by: str = "",
    pick: str = "",
    geometry: str = "",
    coordinates: str = "",
    georel: str = "",
    format: str = "",
    options: str = "",
    aggr_methods: str = "",
    did: str = "",
) -> dict:
    """Search temporal data for an IUDX resource (GET /ngsi-ld/v1/temporal/entities).

    Retrieves time-series data with optional spatial and attribute filters.

    Args:
        resource_id:   UUID of the IUDX resource (dataset ID from catalogue).
        timerel:       Time relationship — one of: between, before, after.
        time_at:       ISO-8601 start timestamp (e.g. "2024-01-01T00:00:00Z").
        token:         Bearer JWT from IUDX Keycloak (required for SECURE/RESTRICTED resources).
        end_time_at:   ISO-8601 end timestamp (required when timerel=between).
        time_property: Attribute to filter on — observationDateTime (default) or observedAt.
        limit:         Max records to return (default 100).
        offset:        Skip first N records (default 0). limit+offset ≤ 10 000.
        last_n:        Return only the last N observations (overrides limit/offset).
        count:         If true, include total count in response.
        q:             Attribute filter expression e.g. "speed>30.0;temperature<=25".
        omit:          Comma-separated properties to exclude (max 5).
        order_by:      Comma-separated sort fields e.g. "observationDateTime:desc".
        pick:          Comma-separated properties to include (max 5).
        geometry:      GeoJSON geometry type — Point, Polygon, LineString, bbox.
        coordinates:   Coordinate string matching geometry type.
        georel:        Spatial relation e.g. "near;maxDistance=1000", "within", "intersects".
        format:        Response format — "simplified" strips NGSI-LD wrappers.
        options:       "aggregatedValues" enables statistical aggregation.
        aggr_methods:  Comma-separated aggregation methods when options=aggregatedValues
                       (totalCount, distinctCount, min, max, sum, avg, stddev).
        did:           Optional delegation ID header for delegated access.
    """
    params: dict[str, Any] = {
        "id": resource_id,
        "timerel": timerel,
        "timeAt": time_at,
        "timeproperty": time_property,
        "limit": limit,
        "offset": offset,
        "count": str(count).lower(),
    }
    if end_time_at:
        params["endTimeAt"] = end_time_at
    if last_n:
        params["lastN"] = last_n
    if q:
        params["q"] = q
    if omit:
        params["omit"] = omit
    if order_by:
        params["orderBy"] = order_by
    if pick:
        params["pick"] = pick
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if georel:
        params["georel"] = georel
    if format:
        params["format"] = format
    if options:
        params["options"] = options
    if aggr_methods:
        params["aggrMethods"] = aggr_methods
    return await _rs_get("/ngsi-ld/v1/temporal/entities", token=token, did=did, params=params)


@mcp.tool()
async def rs_post_temporal_query(
    query_json: str,
    token: str,
    limit: int = 100,
    offset: int = 0,
    count: bool = False,
    format: str = "",
    did: str = "",
) -> dict:
    """Temporal POST search combining time, spatial, and attribute filters
    (POST /ngsi-ld/v1/temporal/entityOperations/query).

    Use this when your query is too complex for URL parameters.

    Args:
        query_json: JSON string with the query body. Example:
            {
              "type": "Query",
              "entities": [{"id": "<resource-uuid>"}],
              "temporalQ": {
                "timerel": "between",
                "timeAt": "2024-01-01T00:00:00Z",
                "endTimeAt": "2024-01-08T00:00:00Z",
                "timeproperty": "observationDateTime"
              },
              "geoQ": {
                "geometry": "Point",
                "coordinates": [72.834, 21.178],
                "georel": "near;maxDistance=1000",
                "geoproperty": "location"
              },
              "q": "speed>30.0",
              "pick": "id,speed,observationDateTime"
            }
        token:  Bearer JWT.
        limit:  Max records (default 100).
        offset: Skip N records (default 0).
        count:  Include total count in response.
        format: "simplified" to strip NGSI-LD wrappers.
        did:    Optional delegation ID header.
    """
    body = _parse(query_json, "query_json")
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if count:
        params["count"] = str(count).lower()
    if format:
        params["format"] = format
    return await _rs_post(
        "/ngsi-ld/v1/temporal/entityOperations/query",
        token=token, did=did, params=params, body=body,
    )


@mcp.tool()
async def rs_get_entities(
    resource_id: str,
    token: str,
    limit: int = 100,
    offset: int = 0,
    count: bool = False,
    order_by: str = "",
    q: str = "",
    omit: str = "",
    pick: str = "",
    geometry: str = "",
    coordinates: str = "",
    georel: str = "",
    format: str = "",
    did: str = "",
) -> dict:
    """Spatial and attribute entity search (GET /ngsi-ld/v1/entities).

    Retrieves the latest snapshot of entities matching spatial/attribute filters.

    Args:
        resource_id:  UUID of the IUDX resource.
        token:        Bearer JWT.
        limit:        Max records (default 100).
        offset:       Skip N records (default 0).
        count:        Include total count.
        order_by:     Comma-separated sort fields.
        q:            Attribute filter e.g. "temperature>25;humidity<80".
        omit:         Properties to exclude (max 5, comma-separated).
        pick:         Properties to include (max 5, comma-separated).
        geometry:     GeoJSON geometry type.
        coordinates:  Coordinate string.
        georel:       Spatial relation.
        format:       "simplified" strips NGSI-LD wrappers.
        did:          Optional delegation ID header.
    """
    params: dict[str, Any] = {
        "id": resource_id,
        "limit": limit,
        "offset": offset,
        "count": str(count).lower(),
    }
    if order_by:
        params["orderBy"] = order_by
    if q:
        params["q"] = q
    if omit:
        params["omit"] = omit
    if pick:
        params["pick"] = pick
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if georel:
        params["georel"] = georel
    if format:
        params["format"] = format
    return await _rs_get("/ngsi-ld/v1/entities", token=token, did=did, params=params)


@mcp.tool()
async def rs_post_entities_query(
    query_json: str,
    token: str,
    limit: int = 100,
    offset: int = 0,
    count: bool = False,
    format: str = "",
    did: str = "",
) -> dict:
    """Spatial/attribute POST search (POST /ngsi-ld/v1/entityOperations/query).

    Use when spatial or attribute filters are too complex for URL parameters.

    Args:
        query_json: JSON string. Example:
            {
              "type": "Query",
              "entities": [{"id": "<resource-uuid>"}],
              "geoQ": {
                "geometry": "Point",
                "coordinates": [72.834, 21.178],
                "georel": "near;maxDistance=1000",
                "geoproperty": "location"
              },
              "q": "speed>30.0",
              "pick": "id,speed"
            }
        token:  Bearer JWT.
        limit:  Max records (default 100).
        offset: Skip N records (default 0).
        count:  Include total count.
        format: "simplified" to strip NGSI-LD wrappers.
        did:    Optional delegation ID header.
    """
    body = _parse(query_json, "query_json")
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if count:
        params["count"] = str(count).lower()
    if format:
        params["format"] = format
    return await _rs_post(
        "/ngsi-ld/v1/entityOperations/query",
        token=token, did=did, params=params, body=body,
    )


@mcp.tool()
async def rs_get_latest_entity_data(
    resource_id: str,
    token: str,
    page: int = 1,
    size: int = 10,
    time_rel: str = "",
    time: str = "",
    end_time: str = "",
    sort: str = "",
    did: str = "",
) -> dict:
    """Retrieve the latest data for a resource (GET /ngsi-ld/v2/entities/{id}).

    Returns the most recent observations/records for the given resource ID.

    Args:
        resource_id: UUID of the IUDX resource (path parameter).
        token:       Bearer JWT.
        page:        Page number (default 1).
        size:        Results per page (default 10).
        time_rel:    Optional time filter — between, before, after, during.
        time:        ISO-8601 start time (required when time_rel is set).
        end_time:    ISO-8601 end time (required when time_rel=between/during).
        sort:        Sort order — e.g. "observationDateTime:desc" or "itemCreatedAt:asc".
        did:         Optional delegation ID header.
    """
    params: dict[str, Any] = {"page": page, "size": size}
    if time_rel:
        params["timeRel"] = time_rel
    if time:
        params["time"] = time
    if end_time:
        params["endTime"] = end_time
    if sort:
        params["sort"] = sort
    return await _rs_get(f"/ngsi-ld/v2/entities/{resource_id}", token=token, did=did, params=params)


@mcp.tool()
async def rs_search_entity_data(
    resource_id: str,
    search_criteria_json: str,
    token: str,
    page: int = 1,
    size: int = 100,
    sort: str = "",
    did: str = "",
) -> dict:
    """Advanced multi-criteria search for a resource (POST /ngsi-ld/v2/entities/{id}/search).

    Supports property (term), numeric range, temporal, and geo-spatial filters.

    Args:
        resource_id:          UUID of the IUDX resource.
        search_criteria_json: JSON string with search body. Examples:

            Text search:
            {"q": "temperature sensor", "fuzzy": true}

            Term + temporal filter:
            {
              "searchCriteria": [
                {"searchType": "term", "field": "deviceType", "values": ["weatherStation"]},
                {"searchType": "betweenTemporal", "field": "observationDateTime",
                 "values": ["2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"]}
              ],
              "filter": ["id", "observationDateTime", "temperature"]
            }

            Range filter:
            {
              "searchCriteria": [
                {"searchType": "betweenRange", "field": "temperature", "values": [20, 35]},
                {"searchType": "afterRange", "field": "humidity", "values": [60]}
              ]
            }

            Geo-spatial:
            {
              "geoQ": {
                "geometry": "Point",
                "coordinates": [72.834, 21.178],
                "georel": "near;maxDistance=5000",
                "geoproperty": "location"
              }
            }

        token: Bearer JWT.
        page:  Page number (default 1).
        size:  Results per page (default 100).
        sort:  Sort expression — up to 3 fields semicolon-separated
               e.g. "observationDateTime:desc;temperature:asc".
        did:   Optional delegation ID header.
    """
    body = _parse(search_criteria_json, "search_criteria_json")
    params: dict[str, Any] = {"page": page, "size": size}
    if sort:
        params["sort"] = sort
    return await _rs_post(
        f"/ngsi-ld/v2/entities/{resource_id}/search",
        token=token, did=did, params=params, body=body,
    )


@mcp.tool()
async def rs_download_entity_data(
    resource_id: str,
    token: str,
    sort: str = "",
    did: str = "",
) -> str:
    """Download all data for a resource as CSV (GET /ngsi-ld/v2/{id}/download).

    Returns raw CSV text. Use for bulk exports when JSON pagination is impractical.

    Args:
        resource_id: UUID of the IUDX resource.
        token:       Bearer JWT.
        sort:        Sort order e.g. "observationDateTime:desc".
        did:         Optional delegation ID header.
    """
    params: dict[str, Any] = {}
    if sort:
        params["sort"] = sort
    return await _rs_get_text(f"/ngsi-ld/v2/{resource_id}/download", token=token, did=did, params=params)


@mcp.tool()
async def rs_download_entity_data_post(
    resource_id: str,
    search_criteria_json: str,
    token: str,
    sort: str = "",
    did: str = "",
) -> str:
    """Download filtered data for a resource as CSV (POST /ngsi-ld/v2/{id}/download).

    Same search body format as rs_search_entity_data but returns CSV text.

    Args:
        resource_id:          UUID of the IUDX resource.
        search_criteria_json: JSON string with search criteria (same format as rs_search_entity_data).
        token:                Bearer JWT.
        sort:                 Sort expression (up to 3 semicolon-separated fields).
        did:                  Optional delegation ID header.
    """
    body = _parse(search_criteria_json, "search_criteria_json")
    params: dict[str, Any] = {}
    if sort:
        params["sort"] = sort
    return await _rs_post_text(
        f"/ngsi-ld/v2/{resource_id}/download",
        token=token, did=did, params=params, body=body,
    )


@mcp.tool()
async def rs_create_elasticsearch_index(
    index_config_json: str,
    token: str,
) -> dict:
    """Create an Elasticsearch index for a dataset (POST /admin/elasticsearch/createIndex).

    Admin-only operation. Creates the backing search index for a new resource.
    If ES_INDEX_PREFIX is set, it is automatically prepended to the index id.

    Args:
        index_config_json: JSON string with index configuration. Example:
            {
              "id": "<dataset-uuid>",
              "dataDescriptor": {
                "temperature": {"type": "float"},
                "humidity": {"type": "float"},
                "observationDateTime": {"type": "date"},
                "location": {"type": "geo_point"}
              }
            }
        token: Bearer JWT with admin privileges.
    """
    body = _parse(index_config_json, "index_config_json")
    if ES_INDEX_PREFIX and "id" in body:
        body["id"] = f"{ES_INDEX_PREFIX}{body['id']}"
    return await _rs_post("/admin/elasticsearch/createIndex", token=token, body=body)


@mcp.tool()
async def rs_ingest_entities(
    data_json: str,
    token: str,
) -> dict:
    """Publish data to IUDX Resource Server (POST /ngsi-ld/v1/ingestion/entities).

    The resource ID must be embedded inside each data object as the "entities" field.
    Use this endpoint when publishing data for multiple resources in a single call.

    Args:
        data_json: JSON array string of data objects. Example:
            [
              {
                "entities": "<resource-uuid>",
                "observationDateTime": "2024-01-15T10:30:00+05:30",
                "temperature": 28.5,
                "humidity": 65.2,
                "deviceInfo": {"deviceID": "SENSOR_001"}
              }
            ]
        token: Bearer JWT with data-ingestion privileges.
    """
    body = _parse(data_json, "data_json")
    return await _rs_post("/ngsi-ld/v1/ingestion/entities", token=token, body=body)


@mcp.tool()
async def rs_ingest_entities_on_seek(
    resource_id: str,
    data_json: str,
    token: str,
) -> dict:
    """Publish data with on-seek support (POST /ngsi-ld/v1/ingestion/entities/{id}/on-seek).

    Enables seekable streaming ingestion for the specified resource.
    The resource ID is specified as a path parameter (not in the body).

    Args:
        resource_id: UUID of the IUDX resource.
        data_json:   JSON array string of data objects. Example:
            [
              {
                "observationDateTime": "2024-01-15T10:30:00+05:30",
                "currentLevel": 1.16,
                "referenceLevel": 15.9,
                "measuredDistance": 14.74,
                "deviceInfo": {"deviceID": "FWR055"}
              }
            ]
        token: Bearer JWT with data-ingestion privileges.
    """
    body = _parse(data_json, "data_json")
    return await _rs_post(
        f"/ngsi-ld/v1/ingestion/entities/{resource_id}/on-seek",
        token=token, body=body,
    )


@mcp.tool()
async def rs_ingest_entities_publish(
    resource_id: str,
    data_json: str,
    token: str,
) -> dict:
    """Publish data without on-seek (POST /ngsi-ld/v1/ingestion/entities/{id}).

    Standard data ingestion for the specified resource.
    The resource ID is specified as a path parameter.

    Args:
        resource_id: UUID of the IUDX resource.
        data_json:   JSON array string of data objects (no "entities" field needed). Example:
            [
              {
                "observationDateTime": "2024-01-15T10:30:00+05:30",
                "temperature": 28.5,
                "humidity": 65.2,
                "deviceInfo": {"deviceID": "SENSOR_001"}
              }
            ]
        token: Bearer JWT with data-ingestion privileges.
    """
    body = _parse(data_json, "data_json")
    return await _rs_post(
        f"/ngsi-ld/v1/ingestion/entities/{resource_id}",
        token=token, body=body,
    )
