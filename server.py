# server.py
"""
MCP Server for Wowza Streaming Functions using Model Context Protocol.
Supports both HTTP and STDIO transport modes (run one at a time).
"""
import os
import sys
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP
mcp = FastMCP("StreamingEngine")

# Configuration (server-specific settings, not client credentials)
CONFIG = {
    "host": os.getenv("MCP_HOST", "0.0.0.0"),
    "port": int(os.getenv("MCP_PORT", 8002)),

    "WOWZA_ENGINE_SERVER_NAME": os.getenv("WOWZA_ENGINE_SERVER_NAME"),
    "WOWZA_ENGINE_VHOST_NAME": os.getenv("WOWZA_ENGINE_VHOST_NAME"),
    "WOWZA_ENGINE_INSTANCE_NAME": os.getenv("WOWZA_ENGINE_INSTANCE_NAME"),

    "WOWZA_ENGINE_BASE_URL": os.getenv("WOWZA_ENGINE_BASE_URL"),
    "WOWZA_ENGINE_USERNAME": os.getenv("ADMIN_USER"),
    "WOWZA_ENGINE_PASSWORD": os.getenv("ADMIN_PASSWORD"),

    # Optional defaults
    "admin_base_url": os.getenv("WOWZA_ADMIN_BASE_URL"),
    "audience_base_url": os.getenv("WOWZA_AUDIENCE_BASE_URL"),
}

# Import and register tools
from tools import (
    mediacache_tools,
    streaming_engine_tools,
    application_tools,
    license_tools,
    listeners_tools,
    log4j_tools,
    media_caster_tools,
    monitoring_tools,
    publisher_tools,
    restinfo_tools,
    servers_tools,
    server_status_tools,
    transcoder_tools,
    tune_tools,
    user_tools,
    vhost_tools,
)

# Register Wowza tools
streaming_engine_tools.register_tools(mcp, CONFIG)
application_tools.register_tools(mcp, CONFIG)
listeners_tools.register_tools(mcp, CONFIG)
license_tools.register_tools(mcp, CONFIG)
log4j_tools.register_tools(mcp, CONFIG)
mediacache_tools.register_tools(mcp, CONFIG)  # Combined v2/v3 support
media_caster_tools.register_tools(mcp)
monitoring_tools.register_tools(mcp, CONFIG)
publisher_tools.register_tools(mcp, CONFIG)  # Combined v2/v3 support
restinfo_tools.register_tools(mcp, CONFIG)
servers_tools.register_tools(mcp, CONFIG)
server_status_tools.register_tools(mcp, CONFIG)
transcoder_tools.register_tools(mcp, CONFIG)
tune_tools.register_tools(mcp, CONFIG)
user_tools.register_tools(mcp, CONFIG)
vhost_tools.register_tools(mcp, CONFIG)

# Entry point
if __name__ == "__main__":
    # Priority: CLI arg > MCP_MODE env > default (stdio)
    transport = os.getenv("MCP_MODE", "stdio").lower()

    if transport == "http":
        # Add middleware for HTTP mode
        from middleware.auth_middleware import AuthMiddleware
        from middleware.flag_middleware import FlagMiddleware

        # Authentication middleware should be first to prevent unauthorized access
        mcp.add_middleware(AuthMiddleware())
        mcp.add_middleware(FlagMiddleware(transport_mode="http"))

        logger.info("Starting Wowza MCP server in HTTP mode")
        logger.info(f"Server will start on {CONFIG['host']}:{CONFIG['port']}")
        print(f"[DEBUG] Server Host: {CONFIG['host']}")
        print(f"[DEBUG] Server Port: {CONFIG['port']}")
        mcp.run(
            transport="http",
            host=CONFIG["host"],
            port=CONFIG["port"],
        )
    elif transport == "stdio":
        # Add tool filtering middleware for STDIO mode
        from middleware.flag_middleware import FlagMiddleware
        mcp.add_middleware(FlagMiddleware(transport_mode="stdio"))

        logger.info("Starting Wowza MCP server in STDIO mode")
        mcp.run(transport="stdio")
    else:
        logger.error(f"Invalid transport '{transport}', use 'http' or 'stdio'")
        sys.exit(1)
