# tools/restinfo_tools.py
import json
import logging
from typing import Dict, Optional

from api_client.restinfo_api import WowzaRestInfoApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine REST info-related MCP tools.
    """
    client = make_client(WowzaRestInfoApiClient, CONFIG)
    

    @mcp.tool(
        tags={"server-info", "read"},
        description="Retrieves the REST API configuration information, such as API version and build number."
    )
    async def get_wowza_rest_info() -> str:
        """
        Retrieves general information about the REST API interface of the Wowza Streaming Engine.
        """
        result = await client.get_rest_info()
        return json.dumps(result, indent=2)