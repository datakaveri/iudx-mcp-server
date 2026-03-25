from typing import Any
from ._app import mcp, FILES_BASE_URL, _clients, _headers, _files_get, _files_post, _files_put, _parse
import logging
logger = logging.getLogger(__name__)


# ===========================================================================
# Files Connect API Tools
# ===========================================================================

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@mcp.tool()
async def files_health() -> dict:
    """Check Files Connect API health (GET /v1/health).

    No authentication required.

    Returns:
        Status, timestamp, service name, and version.
    """
    url = f"{FILES_BASE_URL}/health"
    logger.info("FILES GET %s", url)
    r = await _clients["files"].get(url, timeout=10)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Databanks — Files
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_databank_files(
    databank_id: str,
    token: str,
    prefix: str = "",
    delimiter: str = "",
    max_keys: int = 0,
    recursive: bool = False,
) -> dict:
    """List files and directories in a databank (POST /v1/databanks/{databankId}/files).

    Access Control: provider, consumer.

    Args:
        databank_id: Databank ID.
        token: Bearer JWT token.
        prefix: Optional key prefix to filter results.
        delimiter: Optional delimiter for grouping keys into directories.
        max_keys: Maximum number of keys to return (0 = server default).
        recursive: When true, returns all files recursively including subdirectories.
    """
    body: dict[str, Any] = {}
    if prefix:
        body["prefix"] = prefix
    if delimiter:
        body["delimiter"] = delimiter
    if max_keys > 0:
        body["maxKeys"] = max_keys
    if recursive:
        body["recursive"] = recursive
    return await _files_post(f"/databanks/{databank_id}/files", token=token, body=body or None)


@mcp.tool()
async def download_databank_file(
    databank_id: str,
    key: str,
    token: str,
    presigned: bool = True,
) -> dict:
    """Download a file from a databank or get a presigned URL (POST /v1/databanks/{databankId}/files/download).

    Access Control: provider, consumer.

    Args:
        databank_id: Databank ID.
        key: File key (S3 object key).
        token: Bearer JWT token.
        presigned: When true (default), returns a presigned URL instead of streaming content.
    """
    return await _files_post(
        f"/databanks/{databank_id}/files/download",
        token=token,
        body={"key": key, "presigned": presigned},
    )


@mcp.tool()
async def get_databank_file_metadata(
    databank_id: str,
    key: str,
) -> dict:
    """Get metadata for a specific file in a databank (POST /v1/databanks/{databankId}/files/metadata).

    Public endpoint — no authentication required.

    Args:
        databank_id: Databank ID.
        key: File key (S3 object key).
    """
    return await _files_post(
        f"/databanks/{databank_id}/files/metadata",
        body={"key": key},
    )


@mcp.tool()
async def delete_databank_file(
    databank_id: str,
    key: str,
    token: str,
) -> dict:
    """Delete a specific file from a databank (POST /v1/databanks/{databankId}/files/delete).

    Access Control: provider, consumer (owner only).

    Args:
        databank_id: Databank ID.
        key: S3 object key to delete.
        token: Bearer JWT token.
    """
    return await _files_post(
        f"/databanks/{databank_id}/files/delete",
        token=token,
        body={"key": key},
    )


@mcp.tool()
async def preview_databank_file(
    databank_id: str,
    key: str,
    token: str,
    max_lines: int = 0,
    file_type: str = "",
) -> dict:
    """Generate a preview of a file in a databank (POST /v1/databanks/{databankId}/files/preview).

    Access Control: provider, consumer.

    Args:
        databank_id: Databank ID.
        key: File key (S3 object key).
        token: Bearer JWT token.
        max_lines: Maximum number of lines to return (0 = server default).
        file_type: File type hint for preview (e.g. 'csv', 'json').
    """
    body: dict[str, Any] = {"key": key}
    if max_lines > 0:
        body["maxLines"] = max_lines
    if file_type:
        body["fileType"] = file_type
    return await _files_post(f"/databanks/{databank_id}/files/preview", token=token, body=body)


# ---------------------------------------------------------------------------
# Databanks — Multipart Uploads
# ---------------------------------------------------------------------------


@mcp.tool()
async def initiate_databank_upload(
    databank_id: str,
    key: str,
    num_parts: int,
    token: str,
    content_type: str = "",
) -> dict:
    """Initiate a multipart upload to a databank (POST /v1/databanks/{databankId}/uploads).

    Returns presigned URLs for each part. Allowed file types: CSV, JSON, TXT,
    Parquet, XLSX, ZIP. Executable files are not permitted.

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        key: S3 object key for the file being uploaded.
        num_parts: Number of parts the file will be split into.
        token: Bearer JWT token.
        content_type: MIME type of the file (e.g. 'text/csv', 'application/json').
    """
    body: dict[str, Any] = {"key": key, "numParts": num_parts}
    if content_type:
        body["contentType"] = content_type
    return await _files_post(f"/databanks/{databank_id}/uploads", token=token, body=body)


@mcp.tool()
async def complete_databank_upload(
    databank_id: str,
    upload_id: str,
    key: str,
    parts_json: str,
    token: str,
) -> dict:
    """Complete a multipart upload to a databank (PUT /v1/databanks/{databankId}/uploads/{uploadId}).

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        upload_id: Upload ID returned by initiate_databank_upload.
        key: S3 object key for the file.
        parts_json: JSON array of completed parts, each with partNumber (int) and etag (str).
                    Example: '[{"partNumber": 1, "etag": "abc123"}, {"partNumber": 2, "etag": "def456"}]'
        token: Bearer JWT token.
    """
    parts = _parse(parts_json, "parts_json")
    return await _files_put(
        f"/databanks/{databank_id}/uploads/{upload_id}",
        token=token,
        body={"key": key, "parts": parts},
    )


@mcp.tool()
async def cancel_databank_upload(
    databank_id: str,
    upload_id: str,
    key: str,
    token: str,
) -> dict:
    """Cancel an in-progress multipart upload (POST /v1/databanks/{databankId}/uploads/{uploadId}/cancel).

    Removes any already-uploaded parts.

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        upload_id: Upload ID to cancel.
        key: S3 object key.
        token: Bearer JWT token.
    """
    return await _files_post(
        f"/databanks/{databank_id}/uploads/{upload_id}/cancel",
        token=token,
        body={"key": key},
    )


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


@mcp.tool()
async def upload_asset(
    file_path: str,
    token: str,
) -> dict:
    """Upload an asset file to the Files Connect service (POST /v1/assets).

    Only PDF and image files are allowed: JPEG, PNG, GIF, WebP, SVG, TIFF, BMP.
    Reads the file from the given local path and uploads it as multipart/form-data.

    Access Control: provider, consumer, cos_admin.

    Args:
        file_path: Absolute local path to the file to upload.
        token: Bearer JWT token.
    """
    import mimetypes
    url = f"{FILES_BASE_URL}/assets"
    logger.info("FILES POST (multipart) %s file=%s", url, file_path)
    mime, _ = mimetypes.guess_type(file_path)
    mime = mime or "application/octet-stream"
    with open(file_path, "rb") as fh:
        filename = file_path.rsplit("/", 1)[-1]
        files = {"file": (filename, fh, mime)}
        r = await _clients["files"].post(url, files=files, headers=_headers(token), timeout=60)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def download_asset(
    key: str,
    token: str,
    expires_in: int = 0,
) -> dict:
    """Get a presigned URL for downloading an asset (POST /v1/assets/download).

    Access Control: provider, cos_admin.

    Args:
        key: Asset key returned by upload_asset.
        token: Bearer JWT token.
        expires_in: Presigned URL expiration in seconds (0 = server default).
    """
    body: dict[str, Any] = {"key": key}
    if expires_in > 0:
        body["expiresIn"] = expires_in
    return await _files_post("/assets/download", token=token, body=body)


# ---------------------------------------------------------------------------
# Databanks — Access & Downloads
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_databank_query_access(
    databank_id: str,
    token: str,
) -> dict:
    """Get temporary AWS STS credentials for direct S3 access to a databank (GET /v1/databanks/{databankId}/query-access).

    Returns short-lived credentials usable with DuckDB, Athena, or any S3 client.
    Session duration is controlled server-side via STS_SESSION_DURATION_IN_SECONDS.

    Access Control: provider, consumer.

    Args:
        databank_id: Databank ID.
        token: Bearer JWT token.
    """
    return await _files_get(f"/databanks/{databank_id}/query-access", token=token)


@mcp.tool()
async def get_databank_download_url(
    databank_id: str,
    token: str,
) -> dict:
    """Get a presigned URL for downloading the full databank as a zip (GET /v1/databanks/{databankId}/download).

    Access Control: provider, consumer.

    Args:
        databank_id: Databank ID.
        token: Bearer JWT token.
    """
    return await _files_get(f"/databanks/{databank_id}/download", token=token)


@mcp.tool()
async def get_databank_report_download_url(
    databank_id: str,
) -> dict:
    """Get a presigned URL for the data readiness report PDF (GET /v1/databanks/{databankId}/report/download).

    Public endpoint — no authentication required.
    Reports are stored at {databankId}/data_readiness_report.pdf and are generated
    by the report worker after a 'report' or 'all' processing job completes.

    Args:
        databank_id: Databank ID.
    """
    return await _files_get(f"/databanks/{databank_id}/report/download")


# ---------------------------------------------------------------------------
# Databanks — Processing Jobs
# ---------------------------------------------------------------------------


@mcp.tool()
async def create_databank_process_job(
    databank_id: str,
    job_type: str,
    token: str,
    prefix: str = "",
) -> dict:
    """Create a processing job for a databank (POST /v1/databanks/{databankId}/process).

    Job types:
    - 'zip': Creates a compressed zip archive of the databank files.
    - 'report': Runs data readiness assessment, producing JSON and PDF reports.
    - 'all': Runs both zip and report; returns jobIds.zip and jobIds.report to poll separately.

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        job_type: One of 'zip', 'report', or 'all'.
        token: Bearer JWT token.
        prefix: Optional S3 key prefix to limit which files are processed (not used for report jobs).
    """
    body: dict[str, Any] = {"type": job_type}
    if prefix:
        body["prefix"] = prefix
    return await _files_post(f"/databanks/{databank_id}/process", token=token, body=body)


@mcp.tool()
async def get_databank_process_job(
    databank_id: str,
    job_id: str,
    token: str,
) -> dict:
    """Get the status of a databank processing job (GET /v1/databanks/{databankId}/process/{jobId}).

    Status values: pending, processing, completed, failed.
    For completed report jobs the result field includes: data_type, files_processed,
    reports_uploaded, and processing_time_seconds.

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        job_id: Job ID returned by create_databank_process_job.
        token: Bearer JWT token.
    """
    return await _files_get(f"/databanks/{databank_id}/process/{job_id}", token=token)


@mcp.tool()
async def update_databank_process_job_status(
    databank_id: str,
    job_id: str,
    status: str,
    token: str,
    progress: float = -1,
    error: str = "",
    result_json: str = "",
) -> dict:
    """Update the status of a databank processing job (PUT /v1/databanks/{databankId}/process/{jobId}/status).

    Primarily used by worker processes. Valid status transitions:
    pending → processing → completed | failed.

    Access Control: provider.

    Args:
        databank_id: Databank ID.
        job_id: Job ID to update.
        status: New status — 'pending', 'processing', 'completed', or 'failed'.
        token: Bearer JWT token.
        progress: Progress percentage 0–100 (-1 to omit the field).
        error: Error message (when status is 'failed').
        result_json: JSON object with result data (for completed report jobs).
                     Keys: success, data_type, files_processed, reports_uploaded,
                     processing_time_seconds, download_time_seconds,
                     framework_time_seconds, upload_time_seconds.
    """
    body: dict[str, Any] = {"status": status}
    if progress >= 0:
        body["progress"] = progress
    if error:
        body["error"] = error
    if result_json:
        body["result"] = _parse(result_json, "result_json")
    return await _files_put(
        f"/databanks/{databank_id}/process/{job_id}/status",
        token=token,
        body=body,
    )
