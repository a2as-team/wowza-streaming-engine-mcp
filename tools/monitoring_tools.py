import json
import logging
from typing import Dict, Optional, Literal

from api_client.monitoring_api import WowzaMonitoringApiClient
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server monitoring and machine statistics-related MCP tools.
    """
    client = make_client(WowzaMonitoringApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"monitoring", "read"},
        description="Retrieves monitoring configuration."
    )
    async def get_wowza_monitoring_config() -> str:
        """
        Retrieves monitoring configuration.

        Examples:
            get_wowza_monitoring_config() → Get current monitoring config
        """
        try:
            result = await client.get_monitoring_config(
                server_name=config["server_name"]
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logging.error(f"Error getting monitoring config: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @mcp.tool(
        tags={"monitoring", "write"},
        description="Updates monitoring configuration."
    )
    async def update_wowza_monitoring_config(enable: bool, debug_enable: bool, database_debug_enable: bool) -> str:
        """
        Updates monitoring configuration.

        Args:
            enable: Enable monitoring
            debug_enable: Enable debug logging
            database_debug_enable: Enable database debug logging

        Examples:
            update_wowza_monitoring_config(True, False, False)
        """
        try:
            payload = {
                "enable": enable,
                "debugEnable": debug_enable,
                "databaseDebugEnable": database_debug_enable
            }

            result = await client.update_monitoring_config(
                server_name=config["server_name"],
                data=payload
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logging.error(f"Error updating monitoring config: {e}")
            return json.dumps({"error": str(e)}, indent=2)

    @mcp.tool(
        tags={"monitoring", "read"},
        annotations={"readOnlyHint": True},
        description="Get machine or server statistics. Use stats_type to specify current or historical, and scope for machine or server."
    )
    async def get_wowza_statistics(
        scope: Literal["machine", "server", "incoming_stream"],
        stats_type: Literal["current", "historical"] = "current",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_frame: Optional[str] = None,
        app_name: Optional[str] = None,
        stream_name: Optional[str] = None
    ) -> str:
        """
        Retrieve statistics for machine, server, or incoming stream.

        Args:
            scope: "machine", "server", or "incoming_stream"
            stats_type: "current" or "historical"
            start_date: For historical - start date in YYYY-MM-DD format
            end_date: For historical - end date in YYYY-MM-DD format
            time_frame: For historical - predefined time frame (e.g., '1d', '7d', '30d')
            app_name: For incoming_stream - application name
            stream_name: For incoming_stream - stream name

        Examples:
            get_wowza_statistics("machine", "current") → Current machine stats
            get_wowza_statistics("machine", "historical", time_frame="7d") → Last 7 days machine stats
            get_wowza_statistics("server", "historical", time_frame="30d") → Last 30 days server stats
            get_wowza_statistics("incoming_stream", "current", app_name="live", stream_name="mystream")
        """
        try:
            if scope == "machine":
                if stats_type == "current":
                    result = await client.get_current_machine_stats(
                        server_name=config["server_name"]
                    )
                else:
                    params = {}
                    if start_date:
                        params["startDate"] = start_date
                    if end_date:
                        params["endDate"] = end_date
                    if time_frame:
                        params["timeframe"] = time_frame

                    if not params:
                        return json.dumps({"error": "For historical stats, you must provide 'start_date' and 'end_date', or a 'time_frame'."}, indent=2)

                    result = await client.get_historic_machine_stats(
                        server_name=config["server_name"],
                        params=params
                    )

                    if isinstance(result, dict) and 'historic' in result:
                        historic_data = result.get('historic')

                        if not historic_data or not isinstance(historic_data, list):
                            return json.dumps({
                                "message": "No historical statistics found for the specified date range.",
                                "requested_parameters": params
                            }, indent=2)

                        if start_date and end_date:
                            try:
                                data_in_range = False
                                for record in historic_data:
                                    if not isinstance(record, dict):
                                        continue
                                    record_date_str = record.get('date')
                                    if record_date_str and isinstance(record_date_str, str):
                                        record_date_only_str = record_date_str.split('T')[0]
                                        if start_date <= record_date_only_str <= end_date:
                                            data_in_range = True
                                            break

                                if not data_in_range:
                                    return json.dumps({
                                        "message": "No historical statistics found for the specified date range.",
                                        "requested_parameters": params,
                                        "note": "The API returned data, but it was outside the requested time frame, which indicates no data is available for the period."
                                    }, indent=2)
                            except (TypeError, KeyError) as e:
                                logging.warning(f"Could not validate date range in historical stats response: {e}. Returning raw data.")

            elif scope == "server":
                if stats_type == "current":
                    return json.dumps({"error": "Current stats not available for server scope. Use 'historical' or use 'machine' scope instead."}, indent=2)

                params = {}
                if start_date is not None:
                    params["startDate"] = start_date
                if end_date is not None:
                    params["endDate"] = end_date
                if time_frame is not None:
                    params["timeframe"] = time_frame

                result = await client.get_historic_server_stats(
                    server_name=config["server_name"],
                    params=params
                )

            elif scope == "incoming_stream":
                if stats_type == "historical":
                    return json.dumps({"error": "Historical stats not available for incoming_stream scope. Use 'current' only."}, indent=2)

                if not app_name or not stream_name:
                    raise ValueError("'app_name' and 'stream_name' are required for incoming_stream scope")

                result = await client.get_incoming_stream_current_stats(
                    server_name=config["server_name"],
                    vhost_name=config["vhost_name"],
                    app_name=app_name,
                    instance_name=config["instance_name"],
                    stream_name=stream_name
                )
            else:
                raise ValueError(f"Invalid scope: {scope}. Must be 'machine', 'server', or 'incoming_stream'")

            return json.dumps(result, indent=2)
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return json.dumps({"error": str(e)}, indent=2)
