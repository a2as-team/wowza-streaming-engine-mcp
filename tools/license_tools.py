# tools/license_tools.py
import json
import logging
from typing import Dict, Optional, List

from api_client.license_api import WowzaLicenseApiClient
from models import ServerLicensesUpdate
from .shared_client_utils import get_engine_config, make_client


def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server license-related MCP tools.
    """
    client = make_client(WowzaLicenseApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"server-license", "read"},
        description="Retrieves the list of installed server licenses."
    )
    async def get_wowza_server_licenses() -> str:
        """
        Retrieves the current license configuration from the Wowza Streaming Engine.
        """
        result = await client.get_server_licenses(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"server-license", "write"},
        description="Updates the server license list. This action replaces the entire existing list of licenses."
    )
    async def update_wowza_server_licenses(licenses: ServerLicensesUpdate) -> str:
        """
        Updates the server license list with the provided keys.

        Args:
            licenses: A list of license key strings to apply to the server.
        """
        payload = licenses.model_dump(exclude_none=True, by_alias=True)
        result = await client.update_server_licenses(
            server_name=config["server_name"],
            data=payload
        )
        return json.dumps(result, indent=2)