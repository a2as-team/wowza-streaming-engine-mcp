import json
import logging
from typing import Dict, Optional

from api_client.transcoder_api import WowzaTranscoderApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine Transcoder-related MCP tools.
    """
    client = make_client(WowzaTranscoderApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"transcoder", "read"},
        description="Retrieves the server's Transcoder information, including license status and usage."
    )
    async def get_wowza_transcoder_info() -> str:
        """
        Retrieves information about the Transcoder addon, such as whether it is available,
        licensed, and the number of licenses in use.
        """
        result = await client.get_transcoder_info(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)