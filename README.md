# IUDX MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for the [Intelligent Universal Data Exchange (IUDX)](https://dataforpublicgood.org.in/technology/) platform. It exposes the full IUDX **Control Plane**, **Resource Server**, **Resource Server Proxy**, **Files Connect**, and **Sandbox Connect** APIs as **115 Tools**, **8 Resources** (+ 1 resource template), and **13 Prompts**, enabling AI assistants (Claude Desktop, Claude Code, and any MCP-compatible client) to discover, access, query, ingest, manage files, and run sandbox notebooks in IUDX datasets, AI models, organisations, and subscriptions through natural language.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
  - [MCP Inspector (development)](#mcp-inspector-development)
  - [Claude Desktop — local](#claude-desktop--local)
  - [Claude Code — local](#claude-code--local)
  - [Stdio (headless)](#stdio-headless)
- [Docker Deployment](#docker-deployment)
  - [Build and run with Docker](#build-and-run-with-docker)
  - [Docker Compose](#docker-compose)
  - [Environment variables](#environment-variables)
  - [Claude Desktop — Docker](#claude-desktop--docker)
  - [Claude Code — Docker](#claude-code--docker)
- [Authentication](#authentication)
- [Tools Reference](#tools-reference)
  - [Catalogue — Public](#catalogue--public)
  - [Catalogue — Mutations](#catalogue--mutations)
  - [Catalogue — Org / Admin](#catalogue--org--admin)
  - [Resource Servers](#resource-servers)
  - [Organisations](#organisations)
  - [Users](#users)
  - [Credits](#credits)
  - [Tokens](#tokens)
  - [Dashboard & Auditing](#dashboard--auditing)
  - [Leaderboard](#leaderboard)
  - [Subscriptions](#subscriptions)
  - [Asset Access Requests](#asset-access-requests)
  - [Compute Requests](#compute-requests)
  - [Resource Server — Data Query](#resource-server--data-query)
  - [Resource Server — Data Ingestion](#resource-server--data-ingestion)
  - [Resource Server Proxy — Spatial Query](#resource-server-proxy--spatial-query)
  - [Resource Server Proxy — Temporal Query](#resource-server-proxy--temporal-query)
  - [Files Connect — Health](#files-connect--health)
  - [Files Connect — Databank Files](#files-connect--databank-files)
  - [Files Connect — Multipart Uploads](#files-connect--multipart-uploads)
  - [Files Connect — Assets](#files-connect--assets)
  - [Files Connect — Databank Access & Downloads](#files-connect--databank-access--downloads)
  - [Files Connect — Processing Jobs](#files-connect--processing-jobs)
  - [Sandbox Connect — Bookings](#sandbox-connect--bookings)
  - [Sandbox Connect — Categories & Slots](#sandbox-connect--categories--slots)
  - [Sandbox Connect — Direct Notebooks](#sandbox-connect--direct-notebooks)
  - [Sandbox Connect — Token Sessions](#sandbox-connect--token-sessions)
  - [Sandbox Connect — JupyterLite & Profile](#sandbox-connect--jupyterlite--profile)
- [Resources Reference](#resources-reference)
- [Prompts Reference](#prompts-reference)
- [Usage Examples](#usage-examples)
- [Example Client](#example-client)
  - [Run modes](#run-modes)
  - [Stdio transport](#stdio-transport)
  - [SSE transport](#sse-transport)
  - [RS tools](#rs-tools)
- [Project Structure](#project-structure)

---

## Prerequisites

### Local development

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| [uv](https://docs.astral.sh/uv/) | any (used by `mcp dev`) |
| Node.js | ≥ 18 (used by MCP Inspector) |

Install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Docker deployment

| Requirement | Version |
|---|---|
| [Docker](https://docs.docker.com/get-docker/) | ≥ 24 |
| [Docker Compose](https://docs.docker.com/compose/) | ≥ 2.20 (bundled with Docker Desktop) |

---

## Installation

```bash
git clone https://github.com/swaminathanvasanth/iudx-mcp-server.git
cd iudx-mcp-server

# Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install "mcp[cli]" httpx
```

Or with `uv`:

```bash
uv venv && uv pip install "mcp[cli]" httpx
```

---

## Running the Server

### MCP Inspector (development)

The MCP Inspector is a browser-based UI for interactively testing all tools, resources, and prompts.

```bash
cd iudx-mcp-server
.venv/bin/mcp dev server.py
```

Open the URL printed in the terminal (e.g. `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=…`) in your browser. The Inspector connects to the server over stdio and lets you invoke any tool with a form UI.

> **Tip:** `mcp dev` requires `uv` to be on your `PATH`. If you see "command not found", run `source $HOME/.local/bin/env` first.

---

### Claude Desktop — local

Add the server to Claude Desktop's MCP configuration file.

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "iudx": {
      "command": "/absolute/path/to/iudx-mcp-server/.venv/bin/python3",
      "args": ["/absolute/path/to/iudx-mcp-server/server.py"]
    }
  }
}
```

Restart Claude Desktop. The IUDX tools will appear in the tool picker.

---

### Claude Code — local

```bash
claude mcp add iudx \
  --command "/absolute/path/to/iudx-mcp-server/.venv/bin/python3" \
  --args "/absolute/path/to/iudx-mcp-server/server.py"
```

Or edit `.claude/settings.json` in your project root:

```json
{
  "mcpServers": {
    "iudx": {
      "command": ".venv/bin/python3",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/iudx-mcp-server"
    }
  }
}
```

---

### Stdio (headless)

Run the server directly over stdio for use with any MCP client:

```bash
.venv/bin/python3 server.py
```

Or via the installed entry point (after `pip install -e .`):

```bash
iudx-mcp-server
```

---

## Docker Deployment

The Docker image runs the server in **SSE transport** mode by default, exposing an HTTP endpoint on port `8000`. This makes it suitable for shared infrastructure, CI environments, or connecting multiple MCP clients simultaneously.

```
MCP_TRANSPORT=sse   →  HTTP SSE on http://host:8000/sse
MCP_TRANSPORT=stdio →  stdin/stdout (use with docker run -i)
```

### Build and run with Docker

```bash
# Build
docker build -t iudx-mcp-server .

# Run (SSE transport — default)
docker run -p 8000:8000 iudx-mcp-server

# Run against a different IUDX environment
docker run -p 8000:8000 \
  -e IUDX_BASE_URL=https://v2.prod.controlplane.iudx.io \
  -e RS_BASE_URL=https://v2.prod.rs.iudx.io \
  -e RSP_BASE_URL=https://v2.prod.rs.iudx.io/rsp \
  -e FILES_BASE_URL=https://v2.dev.file-s3.iudx.io/v1/ \
  -e SANDBOX_BASE_URL=https://v2.dev.sandbox.iudx.io \
  iudx-mcp-server

# Run in stdio mode (for use as a Docker-based MCP client command)
docker run -i --rm -e MCP_TRANSPORT=stdio iudx-mcp-server
```

---

### Docker Compose

Start the server with a single command:

```bash
docker compose up -d
```

The server starts in SSE mode on `http://localhost:8000/sse`.

Other useful commands:

```bash
# Rebuild after code changes
docker compose up -d --build

# View live logs
docker compose logs -f

# Stop
docker compose down

# Point to production IUDX
IUDX_BASE_URL=https://v2.prod.controlplane.iudx.io \
  RS_BASE_URL=https://v2.prod.rs.iudx.io \
  RSP_BASE_URL=https://v2.prod.rs.iudx.io/rsp \
  docker compose up -d
```

---

### Environment variables

All variables can be set in the shell, a `.env` file next to `docker-compose.yml`, or passed with `-e` to `docker run`.

| Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `sse` | Transport mode: `stdio` \| `sse` \| `streamable-http` |
| `MCP_HOST` | `0.0.0.0` | Bind address (SSE / streamable-http only) |
| `MCP_PORT` | `8000` | Listen port (SSE / streamable-http only) |
| `IUDX_BASE_URL` | `https://v2.dev.controlplane.iudx.io` | IUDX Control Plane base URL |
| `RS_BASE_URL` | `https://v2.dev.rs.iudx.io` | IUDX Resource Server base URL |
| `RSP_BASE_URL` | `https://v2.dev.rs.iudx.io/rsp` | IUDX Resource Server Proxy base URL |
| `FILES_BASE_URL` | `https://v2.dev.file-s3.iudx.io/v1` | Files Connect API base URL |
| `SANDBOX_BASE_URL` | `https://v2.dev.sandbox.iudx.io` | Sandbox Connect API base URL (notebooks & bookings) |
| `ES_INDEX_PREFIX` | _(empty)_ | Prefix prepended to all Elasticsearch index names (e.g. `dev-`, `iudx-`) |

**Example `.env` file:**

```env
IUDX_BASE_URL=https://v2.prod.controlplane.iudx.io
RS_BASE_URL=https://v2.prod.rs.iudx.io
RSP_BASE_URL=https://v2.prod.rs.iudx.io/rsp
FILES_BASE_URL=https://v2.dev.file-s3.iudx.io/v1/
SANDBOX_BASE_URL=https://v2.dev.sandbox.iudx.io
MCP_PORT=9000
```

Then run:

```bash
docker compose --env-file .env up -d
```

---

### Claude Desktop — Docker

#### Option A: SSE transport (server already running via Compose)

```json
{
  "mcpServers": {
    "iudx": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

#### Option B: stdio via `docker run` (server started on demand)

```json
{
  "mcpServers": {
    "iudx": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "MCP_TRANSPORT=stdio", "iudx-mcp-server"]
    }
  }
}
```

---

### Claude Code — Docker

#### Option A: SSE transport (server already running via Compose)

```bash
claude mcp add iudx --url http://localhost:8000/sse
```

Or in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "iudx": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

#### Option B: stdio via `docker run`

```bash
claude mcp add iudx \
  --command "docker" \
  --args "run,-i,--rm,-e,MCP_TRANSPORT=stdio,iudx-mcp-server"
```

---

## Authentication

Most Control Plane read endpoints are **public** (no token needed). All Resource Server endpoints require a Bearer JWT. Write operations and org/admin endpoints require specific roles.

Obtain a token with the `get_token` tool:

```json
{
  "tool": "get_token",
  "credentials_json": "{\"username\": \"you@example.com\", \"password\": \"••••••\"}"
}
```

Pass the returned token string as the `token` parameter to any authenticated tool. Roles available:

| Role | Access |
|---|---|
| _(none)_ | Public catalogue search, leaderboard, dashboard |
| `provider` | Create/update own catalogue items |
| `org_admin` | Manage org assets, approve join requests |
| `cos_admin` | Platform-wide admin access |

---

## Tools Reference

### Catalogue — Public

| Tool | HTTP | Description |
|---|---|---|
| `search_catalogue` | `POST /iudx/v2/cat/search` | Full-text, term, temporal, range, and flattened-field search across the public catalogue |
| `get_cat_item` | `GET /iudx/v2/cat/item` | Fetch complete metadata for one item by UUID |
| `get_cat_item_with_access` | `GET /iudx/v2/cat/item/access` | Fetch an item with access-policy enforcement (OPEN / RESTRICTED / PRIVATE) |
| `count_catalogue_entities` | `POST /iudx/v2/cat/count` | Count items grouped by type |
| `list_catalogue_filter_values` | `POST /iudx/v2/cat/list` | List valid values for filter fields (tags, access policy, file format, etc.) |

<details>
<summary><code>search_catalogue</code> — parameter reference</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search_criteria_json` | `str` | required | JSON search body. Text: `{"q": "air quality"}`. Criteria: `{"searchCriteria": [...]}` |
| `filter_fields` | `list[str]` | `null` | Fields to project in the response |
| `token` | `str` | `""` | Optional Bearer JWT |
| `page` | `int` | `1` | Page number |
| `size` | `int` | `20` | Results per page |
| `sort` | `str` | `""` | e.g. `"itemCreatedAt:desc;name:asc"` |

**searchCriteria `searchType` values:**

| searchType | Description |
|---|---|
| `term` | Exact / approximate match (OR across values) |
| `flattenedTerm` | Match in nested fields e.g. `resourceServer.url` |
| `betweenRange` / `beforeRange` / `afterRange` | Numeric range |
| `betweenTemporal` / `beforeTemporal` / `afterTemporal` | ISO-8601 date range |

</details>

---

### Catalogue — Mutations

Require a token with `provider`, `org_admin`, or `cos_admin` role.

| Tool | HTTP | Description |
|---|---|---|
| `create_cat_item` | `POST /iudx/v2/cat/item` | Create a new catalogue item |
| `update_cat_item` | `PUT /iudx/v2/cat/item` | Replace an existing item (include `id` in payload) |
| `delete_cat_item` | `DELETE /iudx/v2/cat/item` | Delete an item by UUID |
| `patch_org_asset` | `PATCH /iudx/v2/cat/organisation/asset` | Update `publishStatus` (ACTIVE / PENDING / DECLINED) or `dataUploadStatus` |

> **Note:** An item is publicly discoverable only when `publishStatus=ACTIVE` **and** `dataUploadStatus=true`.

---

### Catalogue — Org / Admin

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `list_org_assets` | `GET /iudx/v2/cat/organisation/asset` | `org_admin` | List assets in the caller's organisation |
| `search_org_assets` | `POST /iudx/v2/cat/organisation/asset` | `org_admin` | Search org assets with filters |
| `get_all_platform_assets` | `GET /iudx/v2/cat/getAllAssets` | `cos_admin` | List every asset on the platform |
| `filter_all_platform_assets` | `POST /iudx/v2/cat/getAllAssets` | `cos_admin` | Filter all platform assets |
| `get_my_assets` | `GET /iudx/v2/cat/search/myassets` | any | Fetch the caller's own assets |
| `search_my_assets` | `POST /iudx/v2/cat/search/myassets` | any | Search within the caller's own assets |

---

### Resource Servers

Require `cos_admin` or `org_admin` role.

| Tool | HTTP | Description |
|---|---|---|
| `list_resource_servers` | `GET /iudx/v2/resource_servers` | List all registered resource servers |
| `create_resource_server` | `POST /iudx/v2/resource_servers` | Register a new resource server |
| `get_resource_server` | `GET /iudx/v2/resource_servers/{id}` | Fetch a resource server by ID |
| `delete_resource_server` | `DELETE /iudx/v2/resource_servers/{id}` | Delete a resource server |

---

### Organisations

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `list_organisations` | `GET /iudx/v2/auth/organisations` | `cos_admin` / `org_admin` | List all organisations |
| `get_organisation` | `GET /iudx/v2/auth/organisations/{id}` | optional auth | Get organisation details |
| `list_org_users` | `GET /iudx/v2/auth/organisations/{id}/users` | optional auth | List members of an org |
| `list_org_creation_requests` | `GET /iudx/v2/auth/organisations/requests` | `cos_admin` | List pending org creation requests |
| `submit_org_creation_request` | `POST /iudx/v2/auth/organisations/requests` | any | Submit an org creation request |
| `approve_org_creation_request` | `POST /iudx/v2/auth/organisations/requests/approve` | `cos_admin` | Approve or reject an org creation request |
| `list_org_join_requests` | `GET /iudx/v2/auth/organisations/{id}/join_requests` | `org_admin` | List pending join requests for an org |
| `handle_org_join_request` | `POST /iudx/v2/auth/organisations/{org_id}/join_requests/{req_id}` | `org_admin` | Approve or reject a join request |

---

### Users

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `get_my_profile` | `GET /iudx/v2/auth/user` | any | Fetch the authenticated user's profile |
| `update_my_profile` | `PUT /iudx/v2/auth/user/update` | any | Update profile fields |
| `admin_list_users` | `GET /iudx/v2/auth/admin/user` | `cos_admin` | List all platform users |
| `admin_get_user` | `GET /iudx/v2/auth/admin/user/{id}` | `cos_admin` | Fetch a user by ID |

---

### Credits

| Tool | HTTP | Description |
|---|---|---|
| `get_credit_balance` | `GET /iudx/v2/auth/user/credit/balance` | Get own credit balance |
| `request_credits` | `POST /iudx/v2/auth/credit/request` | Submit a credit top-up request |
| `list_my_credit_requests` | `GET /iudx/v2/auth/user/credit/request` | List own credit requests |
| `admin_list_credit_requests` | `GET /iudx/v2/auth/credit/request` | Admin: list all credit requests |

---

### Tokens

| Tool | HTTP | Description |
|---|---|---|
| `get_token` | `POST /iudx/v2/auth/token` | Obtain or refresh a Bearer JWT. No prior auth needed. |

---

### Dashboard & Auditing

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `get_usage_summary` | `GET /iudx/v2/dashboard/usage-summary` | none | Platform-wide usage metrics |
| `get_consumer_activity` | `GET /iudx/v2/auditing/consumer/activity` | any | Own activity logs with optional time/type filters |
| `admin_get_activity_logs` | `GET /iudx/v2/auditing/admin/activity` | `cos_admin` | All platform activity logs |

---

### Leaderboard

All public — no authentication required.

| Tool | HTTP | Description |
|---|---|---|
| `get_asset_leaderboard` | `GET /iudx/v2/leaderboard/asset` | Top assets by usage |
| `get_provider_leaderboard` | `GET /iudx/v2/leaderboard/provider` | Top data providers |
| `get_org_leaderboard` | `GET /iudx/v2/leaderboard/organization` | Top organisations |

---

### Subscriptions

| Tool | HTTP | Description |
|---|---|---|
| `list_subscriptions` | `GET /iudx/v2/subscriptions` | List own subscriptions |
| `create_subscription` | `POST /iudx/v2/subscriptions` | Create a new subscription |
| `get_subscription` | `GET /iudx/v2/subscriptions/{id}` | Fetch a subscription by ID |
| `update_subscription` | `PUT /iudx/v2/subscriptions/{id}` | Update a subscription |
| `delete_subscription` | `DELETE /iudx/v2/subscriptions/{id}` | Delete a subscription |

---

### Asset Access Requests

| Tool | HTTP | Description |
|---|---|---|
| `list_asset_access_requests` | `GET /iudx/v2/auth/asset/request` | List own access requests |
| `create_asset_access_request` | `POST /iudx/v2/auth/asset/request` | Submit a new access request |
| `update_asset_access_request` | `PUT /iudx/v2/auth/asset/request/{id}` | Update a request |
| `delete_asset_access_request` | `DELETE /iudx/v2/auth/asset/request/{id}` | Delete / cancel a request |

---

### Compute Requests

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `list_my_compute_requests` | `GET /iudx/v2/auth/user/compute/requests` | any | List own compute requests |
| `admin_list_compute_requests` | `GET /iudx/v2/auth/compute/requests` | `cos_admin` | List all platform compute requests |

---

### Control Plane — Additional Endpoints

Apps & tokens, delegation, feedback & interactions, KYC, organisation/user management, provider requests, asset sharing, custom roles, ACL servers, request conversations, CSV reports (`tools/controlplane_extra.py`).

| Tool | HTTP | Description |
|---|---|---|
| `create_app` | `POST /iudx/v2/auth/app` | Create an app (client credentials for an app) with delegated roles |
| `list_apps` | `GET /iudx/v2/auth/app` | List the authenticated user's apps |
| `delete_app` | `DELETE /iudx/v2/auth/app/{appId}` | Delete an app |
| `update_app_status` | `PATCH /iudx/v2/auth/app/{appId}` | Update an app's status |
| `get_jwks` | `GET /iudx/v2/auth/jwks` | Fetch the platform JSON Web Key Set (public keys for validating tokens) |
| `get_app_token` | `POST /iudx/auth/v2/app/token` | Obtain a token for an app using its appId/appSecret (optionally scoped to an item) |
| `create_client_credentials` | `POST /iudx/v2/auth/client` | Create a new clientId/clientSecret pair for the authenticated user |
| `download_admin_activity_report` | `GET /iudx/v2/auditing/reportactivity/admin` | Download the admin activity report as CSV |
| `download_consumer_activity_report` | `GET /iudx/v2/auditing/reportactivity/consumer` | Download the consumer activity report as CSV |
| `patch_cat_item` | `PATCH /iudx/v2/cat/item` | Partially update a catalogue item |
| `download_item_script` | `GET /items/scripts/download/{filename}` | Download a catalogue item's Python script |
| `check_item_name_available` | `GET /iudx/v2/cat/item/available-name` | Check whether a catalogue item name is available |
| `create_compute_request` | `POST /iudx/v2/auth/compute/requests` | Request compute-role access |
| `update_compute_request` | `PUT /iudx/v2/auth/compute/requests/{id}` | Grant or reject a compute request (admin) |
| `delete_compute_request` | `DELETE /iudx/v2/auth/user/compute/requests/{id}` | Delete / cancel one of your own compute requests |
| `download_compute_requests_report` | `GET /iudx/v2/auth/compute/requests/report` | Admin: download compute requests report as CSV |
| `admin_get_user_credit_balance` | `GET /iudx/v2/auth/admin/user/credit/balance/{id}` | Admin: fetch a user's credit balance |
| `delete_credit_request` | `DELETE /iudx/v2/auth/user/credit/request/{id}` | Delete / cancel one of your own credit requests |
| `admin_handle_credit_request` | `PUT /iudx/v2/auth/credit/request` | Admin: grant or reject a credit request |
| `admin_deduct_user_credits` | `PUT /iudx/v2/auth/admin/user/credit/deduct` | Admin: deduct credits from a user |
| `admin_add_user_credits` | `PUT /iudx/v2/auth/admin/user/credit/add` | Admin: add credits to a user |
| `download_credit_requests_report` | `GET /iudx/v2/auth/credit/request/report` | Admin: download credit requests report as CSV |
| `create_delegation` | `POST /iudx/v2/auth/delegation` | Grant a delegation to another user |
| `list_delegations_as_delegate` | `GET /iudx/v2/auth/delegation/delegate` | List delegations granted to you (you are the delegate) |
| `list_delegations_as_delegator` | `GET /iudx/v2/auth/delegation/delegator` | List delegations you have granted (you are the delegator) |
| `download_delegations_report` | `GET /iudx/v2/auth/delegation/delegator/report` | Download the delegator delegations report as CSV |
| `get_delegation` | `GET /iudx/v2/auth/delegation/{id}` | Fetch a delegation grant by ID |
| `delete_delegation` | `PUT /iudx/v2/auth/delegation/{id}` | Delete a delegation grant (delegator only; marks it DELETED) |
| `add_delegation_constraints` | `PATCH /iudx/v2/auth/delegation/{id}/constraints` | Add role constraints to a delegation |
| `remove_delegation_constraints` | `DELETE /iudx/v2/auth/delegation/{id}/constraints` | Remove role constraints from a delegation |
| `reject_delegation` | `POST /iudx/v2/auth/delegation/{id}/reject` | Reject a delegation granted to you (delegate only) |
| `create_user_interaction` | `POST /iudx/v2/user/interactions` | Record a user interaction (bookmark / like / dislike) on an asset |
| `list_user_interactions` | `GET /iudx/v2/user/interactions` | List the user's interactions |
| `sync_user_interactions` | `GET /iudx/v2/user/interactions/sync` | Sync the user's interactions |
| `create_user_feedback` | `POST /iudx/v2/user/feedback` | Submit feedback / a rating for an asset |
| `update_user_feedback` | `PUT /iudx/v2/user/feedback` | Update your feedback / rating for an asset |
| `delete_user_feedback` | `DELETE /iudx/v2/user/feedback` | Delete your feedback for an asset |
| `list_approved_feedback` | `GET /iudx/v2/user/feedback/approved` | List approved feedback |
| `list_platform_feedback` | `GET /iudx/v2/user/feedback/platform` | Admin: list all feedback on the platform |
| `list_my_feedback` | `GET /iudx/v2/user/feedback/user` | List the authenticated user's feedback |
| `moderate_user_feedback` | `PUT /iudx/v2/user/feedback/{id}` | Admin: approve / reject a feedback entry |
| `create_provider_feedback` | `POST /iudx/v2/provider/feedback` | Create provider feedback / FAQ / info for an asset |
| `update_provider_feedback` | `PUT /iudx/v2/provider/feedback` | Replace provider feedback entries for an asset+type |
| `list_provider_feedback` | `GET /iudx/v2/provider/feedback` | List provider feedback for an asset |
| `delete_provider_feedback` | `DELETE /iudx/v2/provider/feedback` | Delete provider feedback for an asset+type |
| `verify_kyc` | `POST /iudx/v2/auth/kyc/verify` | Verify KYC with an authorisation code |
| `confirm_kyc` | `GET /iudx/v2/auth/kyc/confirm/{id}` | Confirm a KYC verification by ID |
| `revoke_kyc` | `POST /iudx/v2/auth/kyc/revoke` | Revoke the authenticated user's KYC |
| `list_my_org_creation_requests` | `GET /iudx/v2/auth/user/organisations/requests` | List your own organisation creation requests |
| `delete_my_org_creation_request` | `DELETE /iudx/v2/auth/user/organisations/requests/{id}` | Delete one of your own organisation creation requests |
| `list_my_org_join_requests` | `GET /iudx/v2/auth/user/organisations/join_requests` | List your own organisation join requests |
| `delete_my_org_join_request` | `DELETE /iudx/v2/auth/user/organisations/join_requests/{id}` | Delete one of your own organisation join requests |
| `submit_org_join_request` | `POST /iudx/v2/auth/organisations/{id}/join_requests` | Request to join an organisation |
| `update_org_join_request_status` | `PATCH /iudx/v2/auth/organisation/join-request/{id}` | Update the status of an organisation join request |
| `update_organisation` | `PUT /iudx/v2/auth/organisations/{id}` | Update an organisation |
| `delete_organisation` | `DELETE /iudx/v2/auth/organisations/{id}` | Delete an organisation |
| `get_org_user` | `GET /iudx/v2/auth/organisations/{id}/users/{user_id}` | Fetch a user within an organisation |
| `update_org_user_role` | `PUT /iudx/v2/auth/organisations/{id}/users/{user_id}` | Change a user's role within an organisation |
| `remove_org_user` | `DELETE /iudx/v2/auth/organisations/{id}/users/{user_id}` | Remove a user from an organisation |
| `list_org_provider_requests` | `GET /iudx/v2/auth/organization/user/provider_requests` | List organisation provider requests |
| `delete_org_provider_request` | `DELETE /iudx/v2/auth/organization/user/provider-requests/{id}` | Delete an organisation provider request |
| `create_org_provider_role_request` | `POST /iudx/v2/auth/organization/user/provider_role/requests` | Request the provider role within your organisation |
| `list_org_provider_role_requests` | `GET /iudx/v2/auth/organization/user/provider_role/requests` | List organisation provider-role requests |
| `update_org_provider_role_request` | `PUT /iudx/v2/auth/organization/user/provider_role/requests/{id}` | Grant or reject a provider-role request |
| `add_org_provider` | `POST /iudx/v2/auth/organization/user/provider` | Make a user a provider in an organisation |
| `download_org_creation_requests_report` | `GET /iudx/v2/auth/organisations/requests/report` | Download organisation creation requests report as CSV |
| `download_organisations_report` | `GET /iudx/v2/auth/organisations/report` | Download organisations report as CSV |
| `download_org_join_requests_report` | `GET /iudx/v2/auth/organisations/{id}/join_requests/report` | Download an organisation's join requests report as CSV |
| `download_provider_role_requests_report` | `GET /iudx/v2/auth/organization/user/provider_role/requests/report` | Download provider-role requests report as CSV |
| `create_platform_provider_request` | `POST /iudx/v2/auth/user/platform/provider-requests` | Request the platform provider role |
| `get_my_platform_provider_request` | `GET /iudx/v2/auth/user/platform/provider-requests` | Fetch your platform provider request |
| `delete_my_platform_provider_request` | `DELETE /iudx/v2/auth/user/platform/provider-requests` | Delete your platform provider request |
| `admin_list_platform_provider_requests` | `GET /iudx/v2/auth/admin/platform/provider-requests` | Admin: list platform provider requests |
| `admin_update_platform_provider_request` | `PATCH /iudx/v2/auth/admin/platform/provider-requests/{id}` | Admin: grant / reject a platform provider request |
| `share_asset` | `POST /iudx/v2/cat/assets/share` | Share an asset with users / organisations |
| `unshare_asset` | `DELETE /iudx/v2/cat/assets/share` | Revoke sharing of an asset |
| `list_asset_shares` | `GET /iudx/v2/cat/assets/share` | List who an asset is shared with |
| `list_assets_shared_with_me` | `GET /iudx/v2/cat/assets/shared-with-me` | List assets shared with the authenticated user |
| `request_custom_role` | `POST /iudx/v2/auth/user/custom/role` | Request a custom role / scope for a user |
| `list_custom_roles` | `GET /iudx/v2/auth/user/custom/role` | List custom role requests |
| `delete_custom_role` | `DELETE /iudx/v2/auth/user/custom/role` | Delete a custom role grant |
| `list_custom_role_requesters` | `GET /auth/v2/custom-role/requester` | List custom-role requesters |
| `change_my_password` | `PUT /iudx/v2/auth/user/password` | Change the authenticated user's password |
| `list_users_basic` | `GET /iudx/v2/auth/user/basic` | List users (basic details) |
| `get_user_basic_by_identifier` | `GET /iudx/v2/auth/user/basic/by-identifier` | Look up a user (basic details) by user ID or email |
| `update_my_account_status` | `POST /iudx/v2/auth/user/update` | Activate / deactivate your own account |
| `admin_update_user_account_status` | `POST /iudx/v2/auth/admin/{id}/update` | Admin: activate / deactivate a user account |
| `delete_my_account` | `DELETE /iudx/v2/auth/user/delete` | Delete the authenticated user's account |
| `create_my_description` | `POST /iudx/v2/auth/user/description/info` | Create the user's profile description |
| `update_my_description` | `PATCH /iudx/v2/auth/user/description/info` | Update the user's profile description |
| `get_my_description` | `GET /iudx/v2/auth/user/description/info` | Fetch the user's profile description |
| `list_acl_servers` | `GET /iudx/v2/acl_servers` | List ACL servers |
| `create_acl_server` | `POST /iudx/v2/acl_servers` | Register an ACL server |
| `get_acl_server` | `GET /iudx/v2/acl_servers/{id}` | Fetch an ACL server by ID |
| `delete_acl_server` | `DELETE /iudx/v2/acl_servers/{id}` | Delete an ACL server by ID |
| `list_request_conversations` | `GET /iudx/v2/requests/{request_id}/conversations` | List conversation messages on a request |
| `post_request_message` | `POST /iudx/v2/requests/{request_id}/conversations` | Post a message on a request conversation |
| `get_request_message` | `GET /iudx/v2/requests/{request_id}/conversations/{msg_id}` | Fetch a conversation message |
| `update_request_message` | `PUT /iudx/v2/requests/{request_id}/conversations/{msg_id}` | Edit a conversation message |
| `delete_request_message` | `DELETE /iudx/v2/requests/{request_id}/conversations/{msg_id}` | Delete a conversation message |
| `reply_to_request_message` | `POST /iudx/v2/requests/{request_id}/conversations/{msg_id}/reply` | Reply to a conversation message |
| `get_token_with_client_credentials` | `POST /iudx/v2/auth/token` | Issue a JWT using clientId/clientSecret headers |

---

### Resource Server — Data Query

These tools call the **IUDX Resource Server** (`RS_BASE_URL`). All require a Bearer JWT. They support [NGSI-LD](https://www.etsi.org/technologies/internet-of-things/ngsi-ld) temporal, spatial, and attribute query patterns.

| Tool | HTTP | Description |
|---|---|---|
| `rs_get_temporal_entities` | `GET /ngsi-ld/v1/temporal/entities` | Time-series query with optional spatial and attribute filters |
| `rs_post_temporal_query` | `POST /ngsi-ld/v1/temporal/entityOperations/query` | Complex temporal + spatial + attribute POST query |
| `rs_get_entities` | `GET /ngsi-ld/v1/entities` | Spatial and attribute entity snapshot query |
| `rs_post_entities_query` | `POST /ngsi-ld/v1/entityOperations/query` | Complex spatial/attribute POST query |
| `rs_get_latest_entity_data` | `GET /ngsi-ld/v2/entities/{id}` | Retrieve the most recent records for a resource |
| `rs_search_entity_data` | `POST /ngsi-ld/v2/entities/{id}/search` | Advanced multi-criteria search (term, range, temporal, geo) |
| `rs_download_entity_data` | `GET /ngsi-ld/v2/{id}/download` | Download all data as CSV |
| `rs_download_entity_data_post` | `POST /ngsi-ld/v2/{id}/download` | Download filtered data as CSV |
| `rs_create_elasticsearch_index` | `POST /admin/elasticsearch/createIndex` | Admin: create backing Elasticsearch index for a dataset |

<details>
<summary><code>rs_get_temporal_entities</code> — parameter reference</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `resource_id` | `str` | required | UUID of the IUDX resource |
| `timerel` | `str` | required | `between` \| `before` \| `after` |
| `time_at` | `str` | required | ISO-8601 start timestamp |
| `token` | `str` | required | Bearer JWT |
| `end_time_at` | `str` | `""` | ISO-8601 end (required when `timerel=between`) |
| `time_property` | `str` | `observationDateTime` | `observationDateTime` or `observedAt` |
| `limit` | `int` | `100` | Max records; `limit+offset ≤ 10 000` |
| `offset` | `int` | `0` | Records to skip |
| `last_n` | `int` | `0` | Return only the last N observations |
| `count` | `bool` | `false` | Include total count in response |
| `q` | `str` | `""` | Attribute filter e.g. `"speed>30.0;temp<=25"` |
| `omit` | `str` | `""` | Comma-separated properties to exclude (max 5) |
| `order_by` | `str` | `""` | Sort e.g. `"observationDateTime:desc"` |
| `pick` | `str` | `""` | Comma-separated properties to include (max 5) |
| `geometry` | `str` | `""` | `Point` \| `Polygon` \| `LineString` \| `bbox` |
| `coordinates` | `str` | `""` | GeoJSON coordinate string |
| `georel` | `str` | `""` | `near;maxDistance=<m>` \| `within` \| `intersects` |
| `format` | `str` | `""` | `"simplified"` strips NGSI-LD wrappers |
| `options` | `str` | `""` | `"aggregatedValues"` for statistical aggregation |
| `aggr_methods` | `str` | `""` | Comma-separated: `totalCount,min,max,avg,sum,stddev,distinctCount` |
| `did` | `str` | `""` | Delegation ID header (optional) |

</details>

<details>
<summary><code>rs_search_entity_data</code> — searchCriteria reference</summary>

| `searchType` | Description | `values` format |
|---|---|---|
| `term` | Exact/fuzzy property match | One or more match values |
| `betweenRange` | Numeric range | `[min, max]` |
| `beforeRange` | Numeric less-than | `[max]` |
| `afterRange` | Numeric greater-than | `[min]` |
| `betweenTemporal` | ISO-8601 date range | `["start", "end"]` |
| `beforeTemporal` | Before a date | `["date"]` |
| `afterTemporal` | After a date | `["date"]` |

</details>

---

### Resource Server — Data Ingestion

| Tool | HTTP | Description |
|---|---|---|
| `rs_ingest_entities` | `POST /ngsi-ld/v1/ingestion/entities` | Publish data; resource ID embedded in each record as `"entities"` field |
| `rs_ingest_entities_on_seek` | `POST /ngsi-ld/v1/ingestion/entities/{id}/on-seek` | Seekable streaming ingestion for a resource |
| `rs_ingest_entities_publish` | `POST /ngsi-ld/v1/ingestion/entities/{id}` | Standard publish; resource ID as path parameter |

All ingestion tools require a Bearer JWT with data-ingestion privileges. Data must be a JSON array with at minimum an `observationDateTime` field (ISO-8601 with timezone offset).

---

### Resource Server Proxy — Spatial Query

These tools call the **IUDX Resource Server Proxy** (`RSP_BASE_URL`) which routes requests through the IUDX data plane proxy layer. Bearer JWT is optional for OPEN resources, required for SECURE resources. Both NGSI-LD v1 and v2 variants are available; v2 adds field projection, ordering, pagination, and format selection.

| Tool | HTTP | Description |
|---|---|---|
| `rsp_get_entities_v1` | `GET /ngsi-ld/v1/entities` | Spatial entity snapshot query (geo filter + attribute filter) |
| `rsp_get_entities_v2` | `GET /ngsi-ld/v2/entities` | Spatial query with pick/omit, ordering, count, and format options |
| `rsp_post_entities_query_v1` | `POST /ngsi-ld/v1/entityOperations/query` | Complex spatial POST query (large polygons, multiple filters) |
| `rsp_post_entities_query_v2` | `POST /ngsi-ld/v2/entityOperations/query` | Enhanced spatial POST query with pagination and projection in query params |

---

### Resource Server Proxy — Temporal Query

| Tool | HTTP | Description |
|---|---|---|
| `rsp_get_temporal_entities_v1` | `GET /ngsi-ld/v1/temporal/entities` | Temporal query using `time`/`endtime` params (NGSI-LD v1) |
| `rsp_get_temporal_entities_v2` | `GET /ngsi-ld/v2/temporal/entities` | Temporal query with `timeAt`/`endTimeAt`, pick/omit, ordering, and format |
| `rsp_post_temporal_query_v1` | `POST /ngsi-ld/v1/temporal/entityOperations/query` | Complex temporal+spatial POST query (v1, uses `time`/`endtime` in body) |
| `rsp_post_temporal_query_v2` | `POST /ngsi-ld/v2/temporal/entityOperations/query` | Enhanced temporal+spatial POST query with full v2 controls |

> **v1 vs v2 time parameters:** v1 GET uses `time`/`endtime`; v2 GET uses `timeAt`/`endTimeAt`. In POST bodies: v1 `temporalQ` uses `time`/`endtime`; v2 `temporalQ` uses `timeAt`/`endTimeAt`.

---

### Files Connect — Health

| Tool | HTTP | Auth | Description |
|---|---|---|---|
| `files_health` | `GET /v1/health` | None | Check if the Files Connect API is running |
| `get_files_encryption_public_key` | `GET /v1/encryption/public-key` | None | Fetch the Files Connect encryption public key |

---

### Files Connect — Databank Files

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `list_databank_files` | `POST /v1/databanks/{id}/files` | provider, consumer | List files and directories in a databank; supports prefix, delimiter, maxKeys, and recursive listing |
| `download_databank_file` | `POST /v1/databanks/{id}/files/download` | provider, consumer | Download a file or get a presigned URL for it |
| `get_databank_file_metadata` | `POST /v1/databanks/{id}/files/metadata` | None (public) | Get size, content type, ETag, and last-modified metadata for a file |
| `delete_databank_file` | `POST /v1/databanks/{id}/files/delete` | provider, consumer (owner) | Delete a file by S3 object key |
| `preview_databank_file` | `POST /v1/databanks/{id}/files/preview` | provider, consumer | Return the first N lines of a file for quick inspection |

---

### Files Connect — Multipart Uploads

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `initiate_databank_upload` | `POST /v1/databanks/{id}/uploads` | provider | Start a multipart upload; returns presigned URLs for each part. Allowed types: CSV, JSON, TXT, Parquet, XLSX, ZIP |
| `complete_databank_upload` | `PUT /v1/databanks/{id}/uploads/{uploadId}` | provider | Finalise a multipart upload by supplying the completed part list |
| `cancel_databank_upload` | `POST /v1/databanks/{id}/uploads/{uploadId}/cancel` | provider | Abort an in-progress upload and discard all uploaded parts |

---

### Files Connect — Assets

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `upload_asset` | `POST /v1/assets` | provider, consumer, cos_admin | Upload a PDF or image file (JPEG, PNG, GIF, WebP, SVG, TIFF, BMP) from a local path |
| `download_asset` | `POST /v1/assets/download` | provider, cos_admin | Get a presigned URL for downloading a previously uploaded asset |

---

### Files Connect — Databank Access & Downloads

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `get_databank_query_access` | `GET /v1/databanks/{id}/query-access` | provider, consumer | Get short-lived AWS STS credentials for direct S3 access (usable with DuckDB, Athena, etc.) |
| `get_databank_download_url` | `GET /v1/databanks/{id}/download` | provider, consumer | Get a presigned URL for downloading the entire databank as a zip archive |
| `get_databank_report_download_url` | `GET /v1/databanks/{id}/report/download` | None (public) | Get a presigned URL for the data readiness report PDF |

---

### Files Connect — Processing Jobs

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `create_databank_process_job` | `POST /v1/databanks/{id}/process` | provider | Queue a processing job: `zip` (archive), `report` (data readiness assessment), or `all` (both) |
| `get_databank_process_job` | `GET /v1/databanks/{id}/process/{jobId}` | provider | Poll job status (`pending` → `processing` → `completed` \| `failed`) and retrieve results |
| `update_databank_process_job_status` | `PUT /v1/databanks/{id}/process/{jobId}/status` | provider | Update job status and progress (used by worker processes) |

<details>
<summary><code>create_databank_process_job</code> — job type reference</summary>

| `job_type` | Description | Response shape |
|---|---|---|
| `zip` | Creates a compressed zip archive of all databank files | Single `jobId` |
| `report` | Runs data readiness assessment (structured or unstructured auto-detection); uploads PDF to `{databankId}/data_readiness_report.pdf` in the reports bucket | Single `jobId` |
| `all` | Runs both zip and report in parallel | `jobIds.zip` and `jobIds.report` — poll each separately |

**Completed report job `result` fields:**

| Field | Description |
|---|---|
| `data_type` | `structured` or `unstructured` |
| `files_processed` | Number of files analysed |
| `reports_uploaded` | Number of report files written |
| `processing_time_seconds` | Total wall-clock time |
| `download_time_seconds` | Time downloading source files |
| `framework_time_seconds` | Time running the assessment framework |
| `upload_time_seconds` | Time uploading report outputs |

</details>

---

### Sandbox Connect — Bookings

These tools call the **Sandbox Connect API** (`SANDBOX_BASE_URL`), which manages CPU/GPU Kubeflow notebook sandboxes through slot bookings. Bookings move through lifecycle states: `scheduled` → `ready` → `active` → `shutting_down` → `completed`, with `cancelled` and `expired` as terminal states. Active-capacity limits count `scheduled`, `ready`, `active`, and `shutting_down`; the weekly quota also counts `completed`.

| Tool | HTTP | Description |
|---|---|---|
| `list_sandbox_bookings` | `GET /v1/bookings` | List the user's bookings with status filter and pagination; `notebookUrl` is present only for active bookings |
| `create_sandbox_booking` | `POST /v1/bookings` | Book a CPU/GPU notebook slot (inserted as `scheduled`); supports preloading a file or cloning a git repo |
| `cancel_sandbox_booking` | `PATCH /v1/bookings/{id}/cancel` | Cancel a `scheduled` booking before resources are provisioned |
| `extend_sandbox_booking` | `PATCH /v1/bookings/{id}/extend` | Extend an `active` booking to the next contiguous slot (once per booking, capacity permitting) |
| `terminate_sandbox_booking` | `PATCH /v1/bookings/{id}/terminate` | End a `ready`/`active`/`shutting_down` session early; marks it `completed` and deletes Notebook/PVC |
| `reset_sandbox_booking` | `PATCH /v1/bookings/{id}/reset` | Reset a stuck booking: `scheduled` → `cancelled`, `ready` → `expired` (with resource cleanup) |

---

### Sandbox Connect — Categories & Slots

| Tool | HTTP | Description |
|---|---|---|
| `list_sandbox_categories` | `GET /v1/categories` | List CPU/GPU booking categories with limits, grace periods, and slot templates |
| `list_available_sandbox_slots` | `GET /v1/slots/available` | Slot-level availability for a category on a date (YYYY-MM-DD, IST) |
| `get_sandbox_slots_calendar` | `GET /v1/slots/calendar` | Day-level availability totals for a category and month (YYYY-MM) |
| `list_sandbox_instance_types` | `GET /v1/notebook/instance-types` | Instance types for GPU-backed categories with display metadata |

---

### Sandbox Connect — Direct Notebooks

Direct notebook management is available when the deployment runs with `API_BOOKINGS_ENABLED=false`; notebooks stay live until stopped or deleted.

| Tool | HTTP | Description |
|---|---|---|
| `create_sandbox_notebook` | `POST /v1/notebook/create` | Create a CPU/GPU notebook directly, without a booking |
| `list_sandbox_notebooks` | `GET /v1/notebook/list` | List the user's notebooks with pagination, ordering, and date filtering |
| `get_sandbox_notebook_status` | `GET /v1/notebook/status/{name}` | Notebook status (`opening`/`running`/`stopped`/`failed`/`orphaned`), resources, events, and linked booking |
| `check_sandbox_notebook_exists` | `GET /v1/notebook/check-exists/{name}` | Check whether a notebook name is already taken |
| `start_sandbox_notebook` | `PATCH /v1/notebook/start` | Start a stopped notebook (removes the Kubeflow stopped annotation) |
| `stop_sandbox_notebook` | `PATCH /v1/notebook/stop` | Stop a running notebook (adds the Kubeflow stopped annotation) |
| `delete_sandbox_notebook` | `DELETE /v1/notebook/delete` | Delete a notebook and its PVC permanently |

---

### Sandbox Connect — Token Sessions

Token sessions exchange the caller's access token for a notebook-scoped delegated refresh token stored in a Kubernetes Secret; browser refresh tokens are never accepted. The `PUT` rotation routes accept only a delegated notebook-client access token belonging to the owner.

| Tool | HTTP | Description |
|---|---|---|
| `create_booking_notebook_token_session` | `POST /v1/bookings/{id}/notebook-token-session` | Create a delegated token session for a booked notebook |
| `rotate_booking_notebook_token` | `PUT /v1/bookings/{id}/notebook-token-session` | Persist a rotated refresh token for a booked notebook after Keycloak rotation |
| `create_notebook_token_session` | `POST /v1/notebook/{name}/notebook-token-session` | Create a delegated token session for a direct notebook |
| `rotate_notebook_token` | `PUT /v1/notebook/{name}/notebook-token-session` | Persist a rotated refresh token for a direct notebook |

---

### Sandbox Connect — JupyterLite & Profile

| Tool | HTTP | Description |
|---|---|---|
| `create_jupyterlite_session` | `POST /v1/jupyterlite/session` | Validate the bearer token and set an HttpOnly cookie for browser JupyterLite launches |
| `create_kubeflow_profile` | `POST /v1/profile/create` | Create the user's Kubeflow Profile CRD (required before notebooks can be provisioned) |

---

## Resources Reference

Resources are **read-only, URI-addressable** data sources backed by public IUDX endpoints. They provide ambient context to an LLM without requiring tool calls.

**Concrete resources** (returned by `list_resources()`):

| URI | Description | Backing Endpoint |
|---|---|---|
| `iudx://catalogue/datasets` | First 100 publicly discoverable DataBank items | `POST /iudx/v2/cat/search` |
| `iudx://catalogue/ai_models` | First 100 publicly discoverable AI Model items | `POST /iudx/v2/cat/search` |
| `iudx://catalogue/apps` | First 100 publicly discoverable App items | `POST /iudx/v2/cat/search` |
| `iudx://dashboard/usage_summary` | Platform-wide usage metrics | `GET /iudx/v2/dashboard/usage-summary` |
| `iudx://leaderboard/assets` | Top assets ranked by usage | `GET /iudx/v2/leaderboard/asset` |
| `iudx://leaderboard/providers` | Top data providers | `GET /iudx/v2/leaderboard/provider` |
| `iudx://leaderboard/organizations` | Top organisations | `GET /iudx/v2/leaderboard/organization` |

**Resource templates** (read by supplying a UUID):

| URI Template | Description | Backing Endpoint |
|---|---|---|
| `iudx://catalogue/datasets/{id}` | Full metadata for a specific item by UUID | `GET /iudx/v2/cat/item` |
| `iudx://rsp/entities/{id}` | Latest 10 entity records for a resource via RSP v2 | `GET /rsp/ngsi-ld/v2/entities` |

---

## Prompts Reference

Prompts are **reusable workflow templates** that instruct an LLM to orchestrate a sequence of tools to complete a named task.

### `explore_dataset`

Explore one specific dataset or summarise all available datasets.

| Parameter | Required | Description |
|---|---|---|
| `id` | no | UUID of a specific item. If omitted, summarises all catalogue types. |

**Example invocation:**
> "Use the `explore_dataset` prompt" → summarises DataBank, AI Models, and Apps from the catalogue resources.

---

### `find_datasets_by_topic`

Search the catalogue for items related to a free-text topic.

| Parameter | Required | Description |
|---|---|---|
| `topic` | yes | Domain description e.g. `"air quality"`, `"traffic flow in Surat"` |
| `item_type` | no | `adex:DataBank` (default) \| `adex:AiModel` \| `adex:Apps` |

---

### `platform_health_summary`

Produces an executive platform report by combining `count_catalogue_entities`, `get_usage_summary`, and all three leaderboards. No parameters.

---

### `request_dataset_access`

Walks through checking access policy and submitting an access request for a restricted dataset.

| Parameter | Required | Description |
|---|---|---|
| `asset_id` | yes | UUID of the restricted catalogue item |

---

### `onboard_as_provider`

Guides a data provider through the full item publication workflow: authentication → drafting payload → `create_cat_item` → `patch_org_asset`.

| Parameter | Required | Description |
|---|---|---|
| `item_json_hint` | no | Partial JSON the user has already drafted |

---

### `audit_my_usage`

Retrieves and analyses the caller's activity logs for a time window.

| Parameter | Required | Description |
|---|---|---|
| `start_time` | no | ISO-8601 start timestamp e.g. `"2025-01-01T00:00:00Z"` |
| `end_time` | no | ISO-8601 end timestamp |

---

### `manage_organisation`

Lists org members, reviews pending join requests, and approves / rejects them interactively.

| Parameter | Required | Description |
|---|---|---|
| `org_id` | no | UUID of the organisation. If omitted, lists all orgs first. |

---

### `subscribe_to_dataset`

Sets up a data subscription: verifies access, then calls `create_subscription`.

| Parameter | Required | Description |
|---|---|---|
| `asset_id` | yes | UUID of the catalogue item to subscribe to |

---

### `query_resource_data`

Guides the user through querying time-series or spatial data from the Resource Server. Chooses between temporal GET, temporal POST (for spatial filters), and latest-data GET based on the user's needs.

| Parameter | Required | Description |
|---|---|---|
| `resource_id` | yes | UUID of the IUDX resource |
| `timerel` | no | Time relationship hint — `between`, `before`, or `after` (default `before`) |
| `time_at` | no | ISO-8601 timestamp hint (defaults to current UTC time) |

---

### `download_resource_data`

Guides the user through downloading resource data as CSV, with optional temporal filtering.

| Parameter | Required | Description |
|---|---|---|
| `resource_id` | yes | UUID of the IUDX resource |
| `start_time` | no | ISO-8601 start for filtering e.g. `"2024-01-01T00:00:00Z"` |
| `end_time` | no | ISO-8601 end for filtering |

---

### `ingest_resource_data`

Guides a data provider through publishing observations to an IUDX resource, including choosing the right ingestion endpoint.

| Parameter | Required | Description |
|---|---|---|
| `resource_id` | yes | UUID of the IUDX resource to publish data to |

---

### `rsp_query_spatial_data`

Guides the user through a spatial entity query via the Resource Server Proxy, choosing between GET (simple) and POST (complex body) endpoints, and offering to refine results.

| Parameter | Required | Description |
|---|---|---|
| `resource_id` | yes | UUID of the IUDX resource |
| `georel` | no | Geo-relationship hint: `within`, `near`, `intersects`, etc. (default `within`) |
| `geometry` | no | Geometry type hint: `Polygon`, `Point`, etc. (default `Polygon`) |
| `coordinates` | no | GeoJSON coordinates string. If omitted, user is asked for them. |

---

### `rsp_query_temporal_data`

Guides the user through a temporal time-series query via the Resource Server Proxy, with optional spatial filtering using a combined POST body.

| Parameter | Required | Description |
|---|---|---|
| `resource_id` | yes | UUID of the IUDX resource |
| `timerel` | no | Temporal relationship: `between`, `before`, or `after` (default `between`) |
| `time_at` | no | ISO-8601 anchor timestamp. If omitted, user is asked. |
| `end_time_at` | no | ISO-8601 end timestamp. Required when `timerel=between`. |

---

## Usage Examples

### Search for open air-quality datasets

```
search_catalogue(
  search_criteria_json='{"q": "air quality", "searchCriteria": [{"searchType": "term", "field": "accessPolicy", "values": ["OPEN"]}]}',
  filter_fields=["id", "name", "organization", "tags"],
  size=10
)
```

### Get total item counts

```
count_catalogue_entities()
# → {"result": [{"adex:DataBank": ..., "adex:AiModel": ..., "adex:Apps": ...}]}
```

### Fetch metadata for a specific item

```
get_cat_item(id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
```

### Authenticate and publish a dataset

```
# 1. Get a token
get_token(credentials_json='{"username": "you@example.com", "password": "secret"}')

# 2. Create the item
create_cat_item(
  item_json='{"type": ["adex:DataBank"], "name": "My Dataset", ...}',
  token="<token from step 1>"
)

# 3. Publish it
patch_org_asset(
  id="<new item UUID>",
  patch_json='{"publishStatus": "ACTIVE", "dataUploadStatus": true}',
  token="<token>"
)
```

### Read a resource

In Claude or any MCP client, attach the resource URI as context:

```
iudx://catalogue/datasets          # list of DataBank items
iudx://catalogue/datasets/<uuid>   # metadata for one item
iudx://leaderboard/assets          # top assets by usage
```

### Query time-series data from the Resource Server

```python
# Get the last 200 temperature readings before a timestamp
rs_get_temporal_entities(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    timerel="before",
    time_at="2024-06-01T00:00:00Z",
    token="<bearer-jwt>",
    limit=200,
    q="temperature>25.0",
    pick="observationDateTime,temperature,humidity",
    format="simplified",
)
```

### Temporal POST query with spatial filter

```python
rs_post_temporal_query(
    query_json='''{
      "type": "Query",
      "entities": [{"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}],
      "temporalQ": {
        "timerel": "between",
        "timeAt": "2024-01-01T00:00:00Z",
        "endTimeAt": "2024-01-07T23:59:59Z",
        "timeproperty": "observationDateTime"
      },
      "geoQ": {
        "geometry": "Point",
        "coordinates": [72.834, 21.178],
        "georel": "near;maxDistance=2000",
        "geoproperty": "location"
      },
      "pick": "id,observationDateTime,speed,location"
    }''',
    token="<bearer-jwt>",
    format="simplified",
)
```

### Get latest data snapshot

```python
rs_get_latest_entity_data(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    token="<bearer-jwt>",
    size=20,
    sort="observationDateTime:desc",
)
```

### Download filtered data as CSV

```python
rs_download_entity_data_post(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    search_criteria_json='''{
      "searchCriteria": [
        {"searchType": "betweenTemporal", "field": "observationDateTime",
         "values": ["2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"]}
      ]
    }''',
    token="<bearer-jwt>",
    sort="observationDateTime:asc",
)
```

### Ingest data into a resource

```python
rs_ingest_entities_publish(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    data_json='[{"observationDateTime": "2024-06-01T10:30:00+05:30", "temperature": 28.5, "humidity": 65.2}]',
    token="<bearer-jwt>",
)
```

### List files in a databank

```python
list_databank_files(
    databank_id="my-databank-id",
    token="<bearer-jwt>",
    prefix="2024/",
    recursive=True,
)
```

### Preview a CSV file

```python
preview_databank_file(
    databank_id="my-databank-id",
    key="2024/data.csv",
    token="<bearer-jwt>",
    max_lines=20,
)
```

### Upload a file using multipart upload

```python
# 1. Initiate — get presigned URLs for each part
initiate_databank_upload(
    databank_id="my-databank-id",
    key="datasets/large_file.csv",
    num_parts=3,
    token="<bearer-jwt>",
    content_type="text/csv",
)
# → returns uploadId and presignedUrl for each part

# 2. Upload each part directly to the presigned URLs (outside MCP)

# 3. Complete
complete_databank_upload(
    databank_id="my-databank-id",
    upload_id="<uploadId from step 1>",
    key="datasets/large_file.csv",
    parts_json='[{"partNumber": 1, "etag": "abc"}, {"partNumber": 2, "etag": "def"}, {"partNumber": 3, "etag": "ghi"}]',
    token="<bearer-jwt>",
)
```

### Run a data readiness report and download the PDF

```python
# 1. Queue the job
create_databank_process_job(
    databank_id="my-databank-id",
    job_type="report",
    token="<bearer-jwt>",
)
# → returns jobId

# 2. Poll until completed
get_databank_process_job(
    databank_id="my-databank-id",
    job_id="<jobId from step 1>",
    token="<bearer-jwt>",
)

# 3. Download the PDF (public — no token needed)
get_databank_report_download_url(databank_id="my-databank-id")
# → returns presigned downloadUrl
```

### Get temporary S3 credentials for DuckDB access

```python
get_databank_query_access(
    databank_id="my-databank-id",
    token="<bearer-jwt>",
)
# → returns accessKeyId, secretAccessKey, sessionToken, expiration, and s3Config
```

### Spatial query via the Resource Server Proxy (RSP v2)

```python
# GET — entities within a polygon
rsp_get_entities_v2(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    georel="within",
    geometry="Polygon",
    coordinates="[[[77.0,12.0],[78.0,12.0],[78.0,13.0],[77.0,13.0],[77.0,12.0]]]",
    q="AQI>100",
    pick="id,observationDateTime,AQI,location",
    format="simplified",
    count=True,
)

# POST — near a point with field projection in body
rsp_post_entities_query_v2(
    query_json='''{
      "entities": [{"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}],
      "geoQ": {
        "georel": "near;maxDistance=500",
        "geometry": "Point",
        "coordinates": [77.5946, 12.9716]
      },
      "pick": "id,observationDateTime,temperature"
    }''',
    limit=50,
    format="simplified",
)
```

### Temporal query via the Resource Server Proxy (RSP v2)

```python
# GET — time range query
rsp_get_temporal_entities_v2(
    resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    timerel="between",
    time_at="2024-01-01T00:00:00Z",
    end_time_at="2024-01-07T23:59:59Z",
    q="temperature>25",
    format="simplified",
    order_by="observationDateTime:asc",
)

# POST — temporal + spatial combined query
rsp_post_temporal_query_v2(
    query_json='''{
      "entities": [{"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}],
      "temporalQ": {
        "timerel": "between",
        "timeAt": "2024-01-01T00:00:00Z",
        "endTimeAt": "2024-01-07T23:59:59Z"
      },
      "geoQ": {
        "georel": "within",
        "geometry": "Polygon",
        "coordinates": [[[77.0,12.0],[78.0,12.0],[78.0,13.0],[77.0,13.0],[77.0,12.0]]]
      }
    }''',
    format="simplified",
    count=True,
)
```

---

## Example Client

`examples/example_client.py` is a self-contained Python script that shows how to connect to the IUDX MCP server programmatically using the official `mcp` Python SDK.

### Run modes

| Mode | Command | When to use |
|---|---|---|
| `stdio` | `python examples/example_client.py stdio` | Local dev — server started automatically as a subprocess |
| `sse` | `python examples/example_client.py sse [url]` | Server already running via Docker / `MCP_TRANSPORT=sse` |
| `http` | `python examples/example_client.py http [url]` | Streamable-HTTP transport (MCP ≥ 1.3) |

### Stdio transport

The simplest way to get started — no server process needed:

```bash
# Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install "mcp[cli]" httpx

# Run the example
python examples/example_client.py stdio
```

Expected output:

```
Transport: stdio  (spawning server.py)

──────────────────────────────────────────────────────────
  Available tools (92 total)
──────────────────────────────────────────────────────────
["search_catalogue", "get_cat_item", ..., "update_databank_process_job_status"]

──────────────────────────────────────────────────────────
  count_catalogue_entities
──────────────────────────────────────────────────────────
{"type": "dx:controlPlane:success", "result": [{"adex:DataBank": 50, ...}]}

✓  Demo complete
```

### SSE transport

Start the server first, then connect:

```bash
# Terminal 1 — start server
MCP_TRANSPORT=sse python server.py

# Terminal 2 — run client
python examples/example_client.py sse http://localhost:8000/sse
```

Or against a Docker deployment:

```bash
docker compose up -d
python examples/example_client.py sse http://localhost:8000/sse
```

### RS tools

The RS tool examples in the client are commented out because they require a Bearer JWT. To enable them:

1. Obtain a token:

```python
result = await session.call_tool("get_token", {
    "credentials_json": '{"username": "you@example.com", "password": "secret"}'
})
token = json.loads(result.content[0].text)["result"]["access_token"]
```

2. Uncomment and fill in the RS section in `example_client.py`:

```python
TOKEN = "<token from step 1>"
RESOURCE_ID = "<uuid from catalogue>"

result = await session.call_tool("rs_get_latest_entity_data", {
    "resource_id": RESOURCE_ID,
    "token": TOKEN,
    "size": 5,
    "sort": "observationDateTime:desc",
})

result = await session.call_tool("rs_get_temporal_entities", {
    "resource_id": RESOURCE_ID,
    "timerel": "between",
    "time_at": "2024-01-01T00:00:00Z",
    "end_time_at": "2024-01-07T23:59:59Z",
    "token": TOKEN,
    "limit": 10,
    "format": "simplified",
})

result = await session.call_tool("rs_download_entity_data", {
    "resource_id": RESOURCE_ID,
    "token": TOKEN,
    "sort": "observationDateTime:asc",
})
# → returns raw CSV text
```

---

## Project Structure

```
iudx-mcp-server/
├── server.py            # MCP server — all tools, resources, and prompts
├── pyproject.toml       # Project metadata and dependencies
├── Dockerfile           # Container image (SSE transport by default)
├── docker-compose.yml   # Single-service Compose stack
├── .dockerignore        # Files excluded from the Docker build context
├── README.md            # This file
└── examples/
    └── example_client.py  # Programmatic MCP client (stdio / SSE / HTTP)
```

### Key design decisions

- **Configurable transport** — `MCP_TRANSPORT=stdio` for local / embedded use; `sse` or `streamable-http` for networked / Docker deployments. Controlled entirely by environment variable, no code change needed.
- **Five base URLs** — `IUDX_BASE_URL` for the Control Plane (catalogue, auth, orgs), `RS_BASE_URL` for the Resource Server (time-series query and ingestion), `RSP_BASE_URL` for the Resource Server Proxy (NGSI-LD v1/v2 spatial and temporal search via the IUDX data plane proxy), `FILES_BASE_URL` for the Files Connect API (file storage, multipart uploads, asset management, and processing jobs), and `SANDBOX_BASE_URL` for the Sandbox Connect API (CPU/GPU notebook bookings and lifecycle). Each can be pointed independently at dev, staging, or production.
- **`json.loads` for complex payloads** — IUDX item bodies and RS query objects are large, schema-variable JSON objects. Accepting them as raw JSON strings (parsed internally with `_parse()`) avoids an explosion of keyword parameters and works for all current and future IUDX entity types.
- **Token as a parameter** — Every authenticated tool accepts an explicit `token: str` argument rather than reading from environment variables, keeping the server stateless and easy to test.
- **Resources are public only** — Resources are URI-addressable and cacheable; only unauthenticated public endpoints are exposed as resources. Auth-gated data is exposed exclusively through tools.
- **ES index prefix** — `ES_INDEX_PREFIX` is automatically prepended to the Elasticsearch index `id` in `rs_create_elasticsearch_index`, allowing the same tool calls to target environment-specific indices (e.g. `dev-`, `staging-`, `iudx-`) without changing the payload.
- **CSV helpers** — RS download endpoints return `text/csv` instead of JSON. Dedicated `_rs_get_text` / `_rs_post_text` helpers handle these and return raw CSV strings with a 120-second timeout.

---

## API Reference

| API | Specification |
|---|---|
| Control Plane | `https://v2.dev.controlplane.iudx.io/apis` |
| Resource Server | `https://v2.dev.rs.iudx.io/apis` |
| Resource Server Proxy | `https://v2.dev.rs.iudx.io/rsp/apis` |
| Files Connect | `https://v2.dev.file-s3.iudx.io/apis` |
| Sandbox Connect | `https://v2.dev.sandbox.iudx.io/apis` |
