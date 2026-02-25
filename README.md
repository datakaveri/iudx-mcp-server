# IUDX MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for the [India Urban Data Exchange (IUDX)](https://iudx.org.in) platform. It exposes the full IUDX Control Plane API as **55 Tools**, **8 Resources**, and **8 Prompts**, enabling AI assistants (Claude Desktop, Claude Code, and any MCP-compatible client) to discover, access, and manage IUDX datasets, AI models, organisations, and subscriptions through natural language.

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
- [Resources Reference](#resources-reference)
- [Prompts Reference](#prompts-reference)
- [Usage Examples](#usage-examples)
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
git clone https://github.com/your-org/iudx-mcp-server.git
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
  iudx-mcp-server

# Run in stdio mode (for use as a Docker-based MCP client command)
docker run -i --rm iudx-mcp-server \
  python server.py
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
IUDX_BASE_URL=https://v2.prod.controlplane.iudx.io docker compose up -d
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

**Example `.env` file:**

```env
IUDX_BASE_URL=https://v2.prod.controlplane.iudx.io
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
      "args": ["run", "-i", "--rm",
               "-e", "MCP_TRANSPORT=stdio",
               "iudx-mcp-server",
               "python", "server.py"]
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
  --args "run,-i,--rm,-e,MCP_TRANSPORT=stdio,iudx-mcp-server,python,server.py"
```

---

## Authentication

Most read endpoints are **public** (no token needed). Write operations and org/admin endpoints require a Bearer JWT issued by the IUDX Keycloak Identity Provider.

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
| `request_credits` | `POST /iudx/v2/auth/user/credit/request` | Submit a credit top-up request |
| `get_credit_request` | `GET /iudx/v2/auth/user/credit/request/{id}` | Fetch a specific credit request |
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
| `get_asset_access_request` | `GET /iudx/v2/auth/asset/request/{id}` | Fetch a request by ID |
| `update_asset_access_request` | `PUT /iudx/v2/auth/asset/request/{id}` | Update a request |
| `delete_asset_access_request` | `DELETE /iudx/v2/auth/asset/request/{id}` | Delete / cancel a request |

---

### Compute Requests

| Tool | HTTP | Role | Description |
|---|---|---|---|
| `list_my_compute_requests` | `GET /iudx/v2/auth/user/compute/requests` | any | List own compute requests |
| `get_compute_request` | `GET /iudx/v2/auth/user/compute/requests/{id}` | any | Fetch a compute request by ID |
| `admin_list_compute_requests` | `GET /iudx/v2/auth/compute/requests` | `cos_admin` | List all platform compute requests |

---

## Resources Reference

Resources are **read-only, URI-addressable** data sources backed by public IUDX endpoints. They provide ambient context to an LLM without requiring tool calls.

| URI | Description | Backing Endpoint |
|---|---|---|
| `iudx://catalogue/datasets` | First 100 publicly discoverable DataBank items | `POST /iudx/v2/cat/search` |
| `iudx://catalogue/datasets/{id}` | Full metadata for a specific item by UUID | `GET /iudx/v2/cat/item` |
| `iudx://catalogue/ai_models` | First 100 publicly discoverable AI Model items | `POST /iudx/v2/cat/search` |
| `iudx://catalogue/apps` | First 100 publicly discoverable App items | `POST /iudx/v2/cat/search` |
| `iudx://dashboard/usage_summary` | Platform-wide usage metrics | `GET /iudx/v2/dashboard/usage-summary` |
| `iudx://leaderboard/assets` | Top assets ranked by usage | `GET /iudx/v2/leaderboard/asset` |
| `iudx://leaderboard/providers` | Top data providers | `GET /iudx/v2/leaderboard/provider` |
| `iudx://leaderboard/organizations` | Top organisations | `GET /iudx/v2/leaderboard/organization` |

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
# → {"result": [{"adex:DataBank": 74, "adex:AiModel": 110, "adex:Apps": 76}]}
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

---

## Project Structure

```
iudx-mcp-server/
├── server.py            # MCP server — all tools, resources, and prompts
├── pyproject.toml       # Project metadata and dependencies
├── Dockerfile           # Container image (SSE transport by default)
├── docker-compose.yml   # Single-service Compose stack
├── .dockerignore        # Files excluded from the Docker build context
└── README.md            # This file
```

### Key design decisions

- **Configurable transport** — `MCP_TRANSPORT=stdio` for local / embedded use; `sse` or `streamable-http` for networked / Docker deployments. Controlled entirely by environment variable, no code change needed.
- **`IUDX_BASE_URL` env var** — Point the server at any IUDX environment (dev, staging, prod) without rebuilding the image.
- **`json.loads` for complex payloads** — IUDX item bodies are large, schema-variable JSON objects. Accepting them as raw JSON strings (parsed internally with `_parse()`) avoids an explosion of keyword parameters and works for all current and future IUDX entity types.
- **Token as a parameter** — Every authenticated tool accepts an explicit `token: str` argument rather than reading from environment variables, keeping the server stateless and easy to test.
- **Resources are public only** — Resources are URI-addressable and cacheable; only unauthenticated public endpoints are exposed as resources. Auth-gated data is exposed exclusively through tools.

---

## API Reference

Full OpenAPI specification: `https://v2.dev.controlplane.iudx.io/apis`
