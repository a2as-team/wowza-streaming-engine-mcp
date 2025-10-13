import json
import logging
from typing import Dict, Optional, Literal

from api_client.log4j_api import WowzaLog4jApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine Log4j-related MCP tools.
    """
    client = make_client(WowzaLog4jApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"log4j", "read"},
        description="Retrieves the Server's current log4j (logging) configuration, listing all loggers and their levels."
    )
    async def get_wowza_log4j_config() -> str:
        """
        Retrieves log4j configuration.

        Examples:
            get_wowza_log4j_config() → Get current log4j config
        """
        result = await client.get_log4j_config(
            server_name=config["server_name"]
        )
        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"log4j", "write"},
        description="Manages log4j operations: reload configuration or set logger level."
    )
    async def manage_wowza_log4j(
        operation: Literal["reload", "set_level"],
        logger_name: Optional[str] = None,
        log_level: Optional[str] = None
    ) -> str:
        """
        Manages log4j operations.

        Args:
            operation: "reload" or "set_level"
            logger_name: Logger name (required for set_level)
            log_level: Log level: debug, info, warn, error, fatal (required for set_level)

        Examples:
            manage_wowza_log4j("reload") → Reload log4j config
            manage_wowza_log4j("set_level", "com.wowza.wms.server.Server", "debug")
        """
        if operation == "reload":
            result = await client.perform_global_log4j_action(
                server_name=config["server_name"],
                action="reload"
            )
        elif operation == "set_level":
            if not logger_name or not log_level:
                raise ValueError("'logger_name' and 'log_level' are required for set_level operation")

            allowed_levels = ["debug", "info", "warn", "error", "fatal"]
            if log_level.lower() not in allowed_levels:
                return json.dumps({"error": f"Invalid log_level. Must be one of: {', '.join(allowed_levels)}"})

            result = await client.perform_logger_action(
                server_name=config["server_name"],
                logger_name=logger_name,
                action=log_level.lower()
            )
        else:
            raise ValueError(f"Invalid operation: {operation}")

        return json.dumps(result, indent=2)
