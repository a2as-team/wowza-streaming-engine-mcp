import json
import logging
from typing import Dict, Optional

from api_client.server_status_api import WowzaServerStatusApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server status-related MCP tools.
    """
    client = make_client(WowzaServerStatusApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"server-status", "read"},
        description="Retrieves a detailed status of the Wowza Streaming Engine server, including version, uptime, memory, and license information."
    )
    async def get_wowza_server_status() -> str:
        """
        Retrieves comprehensive status information for the Wowza Streaming Engine server.
        """
        result = await client.get_server_status(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)