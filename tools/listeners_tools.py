# tools/listeners_tools.py
import json
import logging
from typing import Dict, Optional, List

from api_client.listeners_api import WowzaListenersApiClient
from models import ServerListenersUpdate
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server listener-related MCP tools.
    """
    client = make_client(WowzaListenersApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"server-listener", "read"},
        description="Retrieves the list of configured server listeners."
    )
    async def get_wowza_server_listeners() -> str:
        """
        Retrieves the current server listener configuration from the Wowza Streaming Engine.
        """
        result = await client.get_server_listeners(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"server-listener", "write"},
        description="Updates the server listeners list. This action replaces the entire existing list."
    )
    async def update_wowza_server_listeners(server_listeners: ServerListenersUpdate) -> str:
        """
        Updates the server listeners list with the provided configuration.

        Args:
            server_listeners: A list of listener dictionaries. Each dictionary must contain
                              'baseClass' (the Java class path) and 'order' (an integer).
                              Example: [{"baseClass": "com.wowza.wms.plugin.test.TestServerListener", "order": 0}]
        """
        payload = server_listeners.model_dump(exclude_none=True, by_alias=True)
        result = await client.update_server_listeners(
            server_name=config["server_name"],
            data=payload
        )
        return json.dumps(result, indent=2)