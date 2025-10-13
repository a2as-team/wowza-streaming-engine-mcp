import json
import logging
from typing import Dict, Optional

from api_client.tune_api import WowzaTuneApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server tuning-related MCP tools.
    """
    client = make_client(WowzaTuneApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"monitoring", "read"},
        description="Retrieves the server's performance tuning configuration, including Java heap size and garbage collector settings."
    )
    async def get_wowza_server_tune_config() -> str:
        """
        Retrieves the current and configured performance tuning settings for the Wowza Streaming Engine.
        """
        result = await client.get_server_tune_config(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)