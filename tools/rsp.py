from typing import Any
from ._app import mcp, _rsp_get, _rsp_post, _parse


# ---------------------------------------------------------------------------
# Resource Server Proxy (RSP) tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def rsp_get_entities_v1(
    resource_id: str,
    token: str = "",
    did: str = "",
    georel: str = "",
    geometry: str = "",
    coordinates: str = "",
    geoproperty: str = "",
    q: str = "",
    attrs: str = "",
    limit: int = 0,
    offset: int = 0,
) -> dict:
    """Spatial entity search via RSP v1 (GET /ngsi-ld/v1/entities).

    Searches for entities matching geo and/or attribute filter criteria through
    the IUDX Resource Server Proxy.

    Args:
        resource_id: IUDX resource ID (UUID).
        token:       Optional Bearer JWT. Required for SECURE resources.
        did:         Optional delegation ID header.
        georel:      Geo-relationship: near, within, contains, intersects, equals, disjoint,
                     overlaps. Use 'near;maxDistance=500' for proximity.
        geometry:    Geometry type: Point, Polygon, LineString, etc.
        coordinates: GeoJSON coordinates string, e.g. '[77.5946,12.9716]'.
        geoproperty: Property to apply geo filter on (default: location).
        q:           NGSI-LD query expression, e.g. 'temperature>25;humidity<80'.
        attrs:       Comma-separated list of attribute names to return.
        limit:       Max number of results.
        offset:      Result offset for pagination.
    """
    params: dict[str, Any] = {"id": resource_id}
    if georel:
        params["georel"] = georel
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if geoproperty:
        params["geoproperty"] = geoproperty
    if q:
        params["q"] = q
    if attrs:
        params["attrs"] = attrs
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    return await _rsp_get("/ngsi-ld/v1/entities", token=token, did=did, params=params)


@mcp.tool()
async def rsp_get_entities_v2(
    resource_id: str,
    token: str = "",
    did: str = "",
    georel: str = "",
    geometry: str = "",
    coordinates: str = "",
    geoproperty: str = "",
    q: str = "",
    attrs: str = "",
    pick: str = "",
    omit: str = "",
    limit: int = 0,
    offset: int = 0,
    format: str = "",
    count: bool = False,
    order_by: str = "",
) -> dict:
    """Spatial entity search via RSP v2 (GET /ngsi-ld/v2/entities).

    Enhanced spatial search with additional controls: field projection (pick/omit),
    result ordering, format selection, and total-count option.

    Args:
        resource_id: IUDX resource ID (UUID).
        token:       Optional Bearer JWT. Required for SECURE resources.
        did:         Optional delegation ID header.
        georel:      Geo-relationship: near, within, contains, intersects, etc.
        geometry:    Geometry type: Point, Polygon, LineString, etc.
        coordinates: GeoJSON coordinates string, e.g. '[77.5946,12.9716]'.
        geoproperty: Property to apply geo filter on (default: location).
        q:           NGSI-LD query expression, e.g. 'temperature>25'.
        attrs:       Comma-separated attribute names to return.
        pick:        Comma-separated top-level fields to include in response.
        omit:        Comma-separated top-level fields to exclude from response.
        limit:       Max number of results.
        offset:      Result offset for pagination.
        format:      Response format: 'simplified' or 'ngsi-ld'.
        count:       If True, include total count in response.
        order_by:    Field to sort by, e.g. 'observationDateTime:desc'.
    """
    params: dict[str, Any] = {"id": resource_id}
    if georel:
        params["georel"] = georel
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if geoproperty:
        params["geoproperty"] = geoproperty
    if q:
        params["q"] = q
    if attrs:
        params["attrs"] = attrs
    if pick:
        params["pick"] = pick
    if omit:
        params["omit"] = omit
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if format:
        params["format"] = format
    if count:
        params["count"] = "true"
    if order_by:
        params["orderBy"] = order_by
    return await _rsp_get("/ngsi-ld/v2/entities", token=token, did=did, params=params)


@mcp.tool()
async def rsp_get_temporal_entities_v1(
    resource_id: str,
    timerel: str,
    time: str,
    token: str = "",
    did: str = "",
    end_time: str = "",
    georel: str = "",
    geometry: str = "",
    coordinates: str = "",
    geoproperty: str = "",
    q: str = "",
    attrs: str = "",
    limit: int = 0,
    offset: int = 0,
) -> dict:
    """Temporal entity search via RSP v1 (GET /ngsi-ld/v1/temporal/entities).

    Retrieves time-series data for a resource using NGSI-LD temporal operators.
    Uses 'time' and 'endtime' parameter names (not timeAt/endTimeAt).

    Args:
        resource_id: IUDX resource ID (UUID).
        timerel:     Temporal relationship: between, before, or after.
        time:        ISO-8601 anchor timestamp, e.g. '2024-01-15T00:00:00Z'.
        token:       Optional Bearer JWT. Required for SECURE resources.
        did:         Optional delegation ID header.
        end_time:    ISO-8601 end timestamp. Required when timerel='between'.
        georel:      Optional geo-relationship filter.
        geometry:    Optional geometry type for geo filter.
        coordinates: Optional GeoJSON coordinates for geo filter.
        geoproperty: Property to apply geo filter on.
        q:           NGSI-LD attribute query, e.g. 'temperature>25'.
        attrs:       Comma-separated attributes to return.
        limit:       Max number of results.
        offset:      Result offset for pagination.
    """
    params: dict[str, Any] = {"id": resource_id, "timerel": timerel, "time": time}
    if end_time:
        params["endtime"] = end_time
    if georel:
        params["georel"] = georel
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if geoproperty:
        params["geoproperty"] = geoproperty
    if q:
        params["q"] = q
    if attrs:
        params["attrs"] = attrs
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    return await _rsp_get("/ngsi-ld/v1/temporal/entities", token=token, did=did, params=params)


@mcp.tool()
async def rsp_get_temporal_entities_v2(
    resource_id: str,
    timerel: str,
    time_at: str,
    token: str = "",
    did: str = "",
    end_time_at: str = "",
    time_property: str = "",
    georel: str = "",
    geometry: str = "",
    coordinates: str = "",
    geoproperty: str = "",
    q: str = "",
    attrs: str = "",
    pick: str = "",
    omit: str = "",
    limit: int = 0,
    offset: int = 0,
    format: str = "",
    count: bool = False,
    order_by: str = "",
) -> dict:
    """Temporal entity search via RSP v2 (GET /ngsi-ld/v2/temporal/entities).

    Enhanced temporal search with additional controls: field projection (pick/omit),
    custom time property, result ordering, format selection, and total-count option.

    Args:
        resource_id:   IUDX resource ID (UUID).
        timerel:       Temporal relationship: between, before, or after.
        time_at:       ISO-8601 anchor timestamp, e.g. '2024-01-15T00:00:00Z'.
        token:         Optional Bearer JWT. Required for SECURE resources.
        did:           Optional delegation ID header.
        end_time_at:   ISO-8601 end timestamp. Required when timerel='between'.
        time_property: Name of the time property (default: observationDateTime).
        georel:        Optional geo-relationship filter.
        geometry:      Optional geometry type for geo filter.
        coordinates:   Optional GeoJSON coordinates for geo filter.
        geoproperty:   Property to apply geo filter on.
        q:             NGSI-LD attribute query, e.g. 'temperature>25'.
        attrs:         Comma-separated attributes to return.
        pick:          Comma-separated top-level fields to include in response.
        omit:          Comma-separated top-level fields to exclude from response.
        limit:         Max number of results.
        offset:        Result offset for pagination.
        format:        Response format: 'simplified' or 'ngsi-ld'.
        count:         If True, include total count in response.
        order_by:      Field to sort by, e.g. 'observationDateTime:desc'.
    """
    params: dict[str, Any] = {"id": resource_id, "timerel": timerel, "timeAt": time_at}
    if end_time_at:
        params["endTimeAt"] = end_time_at
    if time_property:
        params["timeproperty"] = time_property
    if georel:
        params["georel"] = georel
    if geometry:
        params["geometry"] = geometry
    if coordinates:
        params["coordinates"] = coordinates
    if geoproperty:
        params["geoproperty"] = geoproperty
    if q:
        params["q"] = q
    if attrs:
        params["attrs"] = attrs
    if pick:
        params["pick"] = pick
    if omit:
        params["omit"] = omit
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if format:
        params["format"] = format
    if count:
        params["count"] = "true"
    if order_by:
        params["orderBy"] = order_by
    return await _rsp_get("/ngsi-ld/v2/temporal/entities", token=token, did=did, params=params)


@mcp.tool()
async def rsp_post_entities_query_v1(
    query_json: str,
    token: str = "",
    did: str = "",
) -> dict:
    """Spatial entity POST query via RSP v1 (POST /ngsi-ld/v1/entityOperations/query).

    Accepts a JSON body with entity IDs, geo filter, and attribute query.
    Equivalent to rsp_get_entities_v1 but supports larger or more complex payloads.

    Args:
        query_json: JSON body string. Example:
            {
              "entities": [{"id": "<resource-uuid>"}],
              "geoQ": {
                "georel": "within",
                "geometry": "Polygon",
                "coordinates": [[[77.0,12.0],[78.0,12.0],[78.0,13.0],[77.0,13.0],[77.0,12.0]]]
              },
              "q": "temperature>25",
              "attrs": "temperature,humidity,observationDateTime"
            }
        token: Optional Bearer JWT. Required for SECURE resources.
        did:   Optional delegation ID header.
    """
    body = _parse(query_json, "query_json")
    return await _rsp_post("/ngsi-ld/v1/entityOperations/query", token=token, did=did, body=body)


@mcp.tool()
async def rsp_post_entities_query_v2(
    query_json: str,
    token: str = "",
    did: str = "",
    limit: int = 0,
    offset: int = 0,
    count: bool = False,
    format: str = "",
    order_by: str = "",
) -> dict:
    """Spatial entity POST query via RSP v2 (POST /ngsi-ld/v2/entityOperations/query).

    Enhanced POST spatial query supporting field projection (pick/omit in body),
    pagination, ordering, format selection, and total-count.

    Args:
        query_json: JSON body string. Example:
            {
              "entities": [{"id": "<resource-uuid>"}],
              "geoQ": {
                "georel": "near;maxDistance=1000",
                "geometry": "Point",
                "coordinates": [77.5946,12.9716]
              },
              "q": "AQI>100",
              "pick": "id,observationDateTime,AQI",
              "omit": "deviceInfo"
            }
        token:    Optional Bearer JWT. Required for SECURE resources.
        did:      Optional delegation ID header.
        limit:    Max number of results.
        offset:   Result offset for pagination.
        count:    If True, include total count in response.
        format:   Response format: 'simplified' or 'ngsi-ld'.
        order_by: Field to sort by, e.g. 'observationDateTime:desc'.
    """
    body = _parse(query_json, "query_json")
    params: dict[str, Any] = {}
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if count:
        params["count"] = "true"
    if format:
        params["format"] = format
    if order_by:
        params["orderBy"] = order_by
    return await _rsp_post(
        "/ngsi-ld/v2/entityOperations/query",
        token=token, did=did, params=params or None, body=body,
    )


@mcp.tool()
async def rsp_post_temporal_query_v1(
    query_json: str,
    token: str = "",
    did: str = "",
) -> dict:
    """Temporal entity POST query via RSP v1 (POST /ngsi-ld/v1/temporal/entityOperations/query).

    Accepts a JSON body combining entity IDs, temporal filter, geo filter, and attribute query.
    Equivalent to rsp_get_temporal_entities_v1 but supports larger payloads.
    Uses 'time' and 'endtime' field names inside the temporalQ block.

    Args:
        query_json: JSON body string. Example:
            {
              "entities": [{"id": "<resource-uuid>"}],
              "temporalQ": {
                "timerel": "between",
                "time": "2024-01-01T00:00:00Z",
                "endtime": "2024-01-07T23:59:59Z"
              },
              "geoQ": {
                "georel": "within",
                "geometry": "Polygon",
                "coordinates": [[[77.0,12.0],[78.0,12.0],[78.0,13.0],[77.0,13.0],[77.0,12.0]]]
              },
              "q": "temperature>25",
              "attrs": "temperature,humidity,observationDateTime"
            }
        token: Optional Bearer JWT. Required for SECURE resources.
        did:   Optional delegation ID header.
    """
    body = _parse(query_json, "query_json")
    return await _rsp_post(
        "/ngsi-ld/v1/temporal/entityOperations/query", token=token, did=did, body=body
    )


@mcp.tool()
async def rsp_post_temporal_query_v2(
    query_json: str,
    token: str = "",
    did: str = "",
    limit: int = 0,
    offset: int = 0,
    count: bool = False,
    format: str = "",
    order_by: str = "",
) -> dict:
    """Temporal entity POST query via RSP v2 (POST /ngsi-ld/v2/temporal/entityOperations/query).

    Enhanced POST temporal query supporting field projection (pick/omit in body),
    custom time property, pagination, ordering, format selection, and total-count.
    Uses 'timeAt' and 'endTimeAt' inside the temporalQ block.

    Args:
        query_json: JSON body string. Example:
            {
              "entities": [{"id": "<resource-uuid>"}],
              "temporalQ": {
                "timerel": "between",
                "timeAt": "2024-01-01T00:00:00Z",
                "endTimeAt": "2024-01-07T23:59:59Z",
                "timeproperty": "observationDateTime"
              },
              "geoQ": {
                "georel": "near;maxDistance=500",
                "geometry": "Point",
                "coordinates": [77.5946,12.9716]
              },
              "q": "AQI>100",
              "pick": "id,observationDateTime,AQI,location"
            }
        token:    Optional Bearer JWT. Required for SECURE resources.
        did:      Optional delegation ID header.
        limit:    Max number of results.
        offset:   Result offset for pagination.
        count:    If True, include total count in response.
        format:   Response format: 'simplified' or 'ngsi-ld'.
        order_by: Field to sort by, e.g. 'observationDateTime:desc'.
    """
    body = _parse(query_json, "query_json")
    params: dict[str, Any] = {}
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset
    if count:
        params["count"] = "true"
    if format:
        params["format"] = format
    if order_by:
        params["orderBy"] = order_by
    return await _rsp_post(
        "/ngsi-ld/v2/temporal/entityOperations/query",
        token=token, did=did, params=params or None, body=body,
    )
