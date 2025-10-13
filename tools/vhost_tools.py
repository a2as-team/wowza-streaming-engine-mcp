import json
import logging
from typing import Dict, Optional, Literal

from api_client.vhost_api import WowzaVhostApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine VHost-related MCP tools.
    """
    client = make_client(WowzaVhostApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"vhost", "read"},
        description="Retrieves VHost information. If no vhost_name provided, returns all VHosts. If vhost_name provided with optional info_type, returns specific VHost information."
    )
    async def get_wowza_vhost(
        vhost_name: Optional[str] = None,
        info_type: Optional[Literal["config", "hostports"]] = None
    ) -> str:
        """
        Retrieves VHost (Virtual Host) information.

        Args:
            vhost_name: Optional VHost name. If None, returns all VHosts.
            info_type: Type of information - "config" (default) or "hostports"

        Examples:
            get_wowza_vhost() → List all VHosts
            get_wowza_vhost("_defaultVHost_") → Get VHost config
            get_wowza_vhost("_defaultVHost_", "hostports") → Get host ports
        """
        if vhost_name is None:
            result = await client.get_vhosts(server_name=config["server_name"])
        elif info_type == "hostports":
            result = await client.get_hostports(
                server_name=config["server_name"],
                vhost_name=vhost_name
            )
        else:
            result = await client.get_vhost(
                server_name=config["server_name"],
                vhost_name=vhost_name
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"vhost", "read"},
        description="Retrieves VHost statistics. Use stats_type to specify current or historical statistics."
    )
    async def get_wowza_vhost_stats(
        vhost_name: str,
        stats_type: Literal["current", "historical"] = "current",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_frame: Optional[str] = None
    ) -> str:
        """
        Retrieves VHost statistics.

        Args:
            vhost_name: The VHost name
            stats_type: "current" or "historical"
            start_date: For historical - start date in YYYY-MM-DD format
            end_date: For historical - end date in YYYY-MM-DD format
            time_frame: For historical - predefined time frame (e.g., '1d', '7d', '30d')

        Examples:
            get_wowza_vhost_stats("_defaultVHost_") → Current stats
            get_wowza_vhost_stats("_defaultVHost_", "historical", time_frame="7d") → Last 7 days
        """
        if stats_type == "current":
            result = await client.get_vhost_current_stats(
                server_name=config["server_name"],
                vhost_name=vhost_name
            )
        else:
            params = {}
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            if time_frame:
                params["timeframe"] = time_frame

            result = await client.get_vhost_historic_stats(
                server_name=config["server_name"],
                vhost_name=vhost_name,
                params=params
            )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"vhost", "read"},
        description="Retrieves transcoder templates for a VHost."
    )
    async def get_wowza_vhost_transcoder_template(
        vhost_name: str,
        template_name: Optional[str] = None
    ) -> str:
        """
        Retrieves transcoder templates for a VHost.

        Args:
            vhost_name: The VHost name
            template_name: Optional template name (currently only lists all)

        Examples:
            get_wowza_vhost_transcoder_template("_defaultVHost_") → List all templates
        """
        result = await client.get_transcoder_templates(
            server_name=config["server_name"],
            vhost_name=vhost_name
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"vhost", "write"},
        description="Manages VHost operations: restart, create transcoder template, or delete transcoder template. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_vhost(
        vhost_name: str,
        operation: Literal["restart", "create_transcoder_template", "delete_transcoder_template"],
        template_name: Optional[str] = None,
        template_data: Optional[Dict] = None
    ) -> str:
        """
        Manages VHost operations.

        WARNING: When using 'delete_transcoder_template' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            vhost_name: The VHost name
            operation: "restart", "create_transcoder_template", or "delete_transcoder_template"
            template_name: Template name (required for transcoder operations)
            template_data: Template configuration (optional for create - uses defaults if not provided)

        Examples:
            manage_wowza_vhost("_defaultVHost_", "restart")
            manage_wowza_vhost("_defaultVHost_", "create_transcoder_template", template_name="mobile-hls")
            manage_wowza_vhost("_defaultVHost_", "delete_transcoder_template", template_name="mobile-hls")
        """
        if operation == "restart":
            result = await client.perform_vhost_action(
                server_name=config["server_name"],
                vhost_name=vhost_name,
                action="restart"
            )
        elif operation == "create_transcoder_template":
            if not template_name:
                raise ValueError("'template_name' is required for create_transcoder_template operation")

            default_template = {
                "enabled": True,
                "description": f"Auto-created transcoder template {template_name}",
                "videoCodecs": [{
                    "codec": "H.264",
                    "id": "source",
                    "videoBitrate": 1500,
                    "videoBitrateCustom": False,
                    "videoCodecImplementation": "MainConcept"
                }],
                "audioCodecs": [{
                    "codec": "AAC",
                    "id": "audio",
                    "audioBitrate": 128,
                    "audioBitrateCustom": False
                }],
                "encodes": [],
                "templates": []
            }

            data = template_data or default_template
            result = await client.create_transcoder_template(
                server_name=config["server_name"],
                vhost_name=vhost_name,
                template_name=template_name,
                data=data
            )
        elif operation == "delete_transcoder_template":
            if not template_name:
                raise ValueError("'template_name' is required for delete_transcoder_template operation")

            result = await client.delete_transcoder_template(
                server_name=config["server_name"],
                vhost_name=vhost_name,
                template_name=template_name
            )
        else:
            raise ValueError(f"Invalid operation: {operation}")

        return json.dumps(result, indent=2)
