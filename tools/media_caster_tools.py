import json
import logging
from typing import Dict, Optional

from api_client.media_caster_api import WowzaMediaCasterApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine MediaCaster-related MCP tools.
    """
    client = make_client(WowzaMediaCasterApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"mediacaster", "read"},
        description="Retrieves MediaCaster information. If no media_caster_name provided, returns all MediaCasters. If media_caster_name provided, returns specific MediaCaster details."
    )
    async def get_wowza_media_caster(
        media_caster_name: Optional[str] = None
    ) -> str:
        """
        Retrieves MediaCaster configuration.

        Args:
            media_caster_name: Optional MediaCaster name. If None, returns all MediaCasters.

        Examples:
            get_wowza_media_caster() → List all MediaCasters
            get_wowza_media_caster("stream1") → Get specific MediaCaster details
        """
        if media_caster_name is None:
            result = await client.get_media_casters(
                server_name=config["server_name"]
            )
        else:
            result = await client.get_media_caster(
                server_name=config["server_name"],
                mediacaster_name=media_caster_name
            )
        return json.dumps(result, indent=2)
