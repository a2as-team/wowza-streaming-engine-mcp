# tools/servers_tools.py
import json
import logging
from typing import Dict, Optional, Literal

from api_client.servers_api import WowzaServersApiClient
from .shared_client_utils import get_engine_config, make_client


def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server configuration and management MCP tools.
    Uses consolidation pattern to minimize tool count while maximizing coverage.
    """
    client = make_client(WowzaServersApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"server-config", "read"},
        description="Retrieves server configuration. Supports listing all servers, getting specific server config, or getting advanced config."
    )
    async def get_wowza_server_config(
        server_name: Optional[str] = None,
        include_advanced: bool = False
    ) -> str:
        """
        Retrieves server configuration with flexible options.

        Args:
            server_name: Optional server name. If None, lists all servers. If provided, gets config for that server.
            include_advanced: If True and server_name is provided, returns advanced configuration instead.

        Examples:
            - get_wowza_server_config() -> List all servers
            - get_wowza_server_config(server_name="_defaultServer_") -> Get server config
            - get_wowza_server_config(server_name="_defaultServer_", include_advanced=True) -> Get advanced config
        """
        if server_name is None:
            # List all servers
            result = await client.get_servers()
        elif include_advanced:
            # Get advanced config
            result = await client.get_server_config_adv(server_name=server_name)
        else:
            # Get regular config
            result = await client.get_server_config(server_name=server_name)

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"server-config", "write"},
        description="Updates server configuration (regular or advanced)."
    )
    async def update_wowza_server_config(
        server_config: Dict,
        server_name: Optional[str] = None,
        advanced: bool = False
    ) -> str:
        """
        Updates server configuration.

        Args:
            server_config: The server configuration data as a dictionary.
            server_name: The server name. Defaults to '_defaultServer_'.
            advanced: If True, updates advanced configuration instead of regular config.

        Examples:
            - update_wowza_server_config(server_config={...}) -> Update regular config
            - update_wowza_server_config(server_config={...}, advanced=True) -> Update advanced config
        """
        srv_name = server_name or config["server_name"]

        if advanced:
            result = await client.update_server_config_adv(
                server_name=srv_name,
                data=server_config
            )
        else:
            result = await client.update_server_config(
                server_name=srv_name,
                data=server_config
            )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"server-action", "write"},
        description="Performs an action on the server: restart, start, stop, heapDump, or stackTrace."
    )
    async def perform_wowza_server_action(
        action: Literal["restart", "start", "stop", "heapDump", "stackTrace"],
        server_name: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Performs an action on the Wowza server.

        Args:
            action: The action to perform. Valid values: restart, start, stop, heapDump, stackTrace.
            server_name: The server name. Defaults to '_defaultServer_'.
            filename: Optional file location for heapDump or stackTrace actions.

        Examples:
            - perform_wowza_server_action(action="restart") -> Restart server
            - perform_wowza_server_action(action="heapDump", filename="/tmp/heap.hprof") -> Create heap dump
        """
        srv_name = server_name or config["server_name"]
        result = await client.perform_server_action(
            server_name=srv_name,
            action=action,
            filename=filename
        )
        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"server-logs", "read"},
        description="Retrieves server log files. Can list all log files, get specific log file contents, or download a log file."
    )
    async def get_wowza_server_log_files(
        server_name: Optional[str] = None,
        log_name: Optional[str] = None,
        download: bool = False,
        order: str = "newestFirst",
        line_count: int = 100,
        tail: Optional[int] = None,
        search: Optional[str] = None,
        filter_str: Optional[str] = None
    ) -> str:
        """
        Retrieves server log files with flexible options.

        Args:
            server_name: The server name. Defaults to '_defaultServer_'.
            log_name: Optional log file name. If None, lists all log files. If provided, gets that log's contents.
            download: If True and log_name is provided, downloads the log file (zipped).
            order: Sort order for file list - 'newestFirst' or 'oldestFirst' (only for list mode).
            line_count: Number of lines to retrieve (only for content mode).
            tail: Get last N lines (only for content mode, overrides line_count).
            search: Search string to filter log lines (only for content mode).
            filter_str: Predefined filters like 'noDebug|noInfo' (only for content mode).

        Examples:
            - get_wowza_server_log_files() -> List all log files
            - get_wowza_server_log_files(log_name="wowzastreamingengine_access.log") -> Get log contents
            - get_wowza_server_log_files(log_name="wowzastreamingengine_access.log", tail=50) -> Last 50 lines
            - get_wowza_server_log_files(log_name="wowzastreamingengine_error.log", download=True) -> Download log
        """
        srv_name = server_name or config["server_name"]

        if log_name is None:
            # List all log files
            result = await client.get_server_log_files(
                server_name=srv_name,
                order=order
            )
        elif download:
            # Download log file
            result = await client.download_server_log_file(
                server_name=srv_name,
                log_name=log_name
            )
        else:
            # Get log file contents
            result = await client.get_server_log_file(
                server_name=srv_name,
                log_name=log_name,
                line_count=line_count,
                tail=tail,
                search=search,
                filter_str=filter_str
            )

        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"server-logs", "read"},
        description="Retrieves server logs by type. Can list available log types or get logs of a specific type."
    )
    async def get_wowza_server_logs(
        server_name: Optional[str] = None,
        log_type: Optional[str] = None,
        line_count: int = 100,
        tail: Optional[int] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Retrieves server logs by type.

        Args:
            server_name: The server name. Defaults to '_defaultServer_'.
            log_type: Optional log type (e.g., 'access', 'error', 'stats'). If None, lists all log types.
            line_count: Number of lines to retrieve (only when log_type is specified).
            tail: Get last N lines (overrides line_count).
            search: Search string to filter log lines.
            start_date: Start date filter in UTC milliseconds.
            end_date: End date filter in UTC milliseconds.

        Examples:
            - get_wowza_server_logs() -> List all log types
            - get_wowza_server_logs(log_type="access") -> Get access logs
            - get_wowza_server_logs(log_type="error", tail=100) -> Last 100 error log lines
        """
        srv_name = server_name or config["server_name"]

        if log_type is None:
            # List all log types
            result = await client.get_server_log_types(server_name=srv_name)
        else:
            # Get logs by type
            result = await client.get_server_logs_by_type(
                server_name=srv_name,
                log_type=log_type,
                line_count=line_count,
                tail=tail,
                search=search,
                start_date=start_date,
                end_date=end_date
            )

        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"server-config", "read"},
        description="Retrieves the list of available source control driver names."
    )
    async def get_wowza_source_driver_names(server_name: Optional[str] = None) -> str:
        """
        Retrieves the list of source control drivers available on the server.

        Args:
            server_name: The server name. Defaults to '_defaultServer_'.

        Example:
            - get_wowza_source_driver_names() -> Get list of driver names
        """
        srv_name = server_name or config["server_name"]
        result = await client.get_source_driver_names(server_name=srv_name)
        return json.dumps(result, indent=2)
