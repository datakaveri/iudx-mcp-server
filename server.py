import logging
import os

from tools._app import mcp

# Import all service modules to register their tools/resources/prompts
import tools.catalogue      # noqa: F401
import tools.controlplane   # noqa: F401
import tools.rs             # noqa: F401
import tools.rsp            # noqa: F401
import tools.resources      # noqa: F401
import tools.prompts        # noqa: F401
import tools.files          # noqa: F401

logger = logging.getLogger(__name__)


def main() -> None:
    from tools._app import BASE_URL, RS_BASE_URL, RSP_BASE_URL, FILES_BASE_URL, ES_INDEX_PREFIX
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    logger.info(
        "Starting IUDX MCP Server — transport=%s base_url=%s rs_base_url=%s rsp_base_url=%s files_base_url=%s es_index_prefix=%r",
        transport, BASE_URL, RS_BASE_URL, RSP_BASE_URL, FILES_BASE_URL, ES_INDEX_PREFIX,
    )
    if transport in ("sse", "streamable-http"):
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport=transport)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
