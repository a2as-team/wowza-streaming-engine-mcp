import json
import logging
from typing import Dict, Optional, Literal

from api_client.streaming_engine_api import WowzaStreamingEngineApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine-related MCP tools.
    """
    client = make_client(WowzaStreamingEngineApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"streaming_engine", "read"},
        description="Get live stream sources (publishers) connected to the Wowza Streaming Engine."
    )
    async def get_wowza_live_sources() -> str:
        """
        Retrieves all active live stream publishers.

        Examples:
            get_wowza_live_sources() → List all connected live sources
        """
        result = await client.get_live_sources(server_name=config["server_name"])
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"streaming_engine", "read"},
        description="Get stream targets (push publishing) for an application or delete a stream target."
    )
    async def get_wowza_stream_targets(app_name: str) -> str:
        """
        Retrieves stream targets for an application.

        Args:
            app_name: The application name

        Examples:
            get_wowza_stream_targets("live") → List all stream targets
        """
        result = await client.get_stream_targets(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"streaming_engine", "write"},
        description="DESTRUCTIVE: Delete stream target. ALWAYS confirm with user before executing."
    )
    async def delete_wowza_stream_target(app_name: str, entry_name: str) -> str:
        """
        Deletes a stream target.

        WARNING: This is a DESTRUCTIVE operation that CANNOT be undone.
        ALWAYS confirm with the user before executing this operation.

        Args:
            app_name: The application name
            entry_name: The stream target entry name

        Examples:
            delete_wowza_stream_target("live", "facebook-target")
        """
        result = await client.delete_stream_target(
            server_name=config["server_name"],
            vhost_name=config["vhost_name"],
            app_name=app_name,
            entry_name=entry_name
        )
        return json.dumps(result, indent=2)
