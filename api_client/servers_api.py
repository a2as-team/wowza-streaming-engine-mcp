import aiohttp
import logging
from typing import Dict, Optional

class WowzaServersApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for server configuration and management operations.
    """
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, logger=None):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL of the Wowza Streaming Engine server,
                            e.g., http://localhost:8087
            username (Optional[str]): The username for authentication.
            password (Optional[str]): The password for authentication.
            logger (function, optional): A logging function. Defaults to a standard logger.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.logger = logger if logger else lambda level, msg: logging.log(getattr(logging, level.upper(), logging.INFO), msg)
        self.logger("info", f"WowzaApiC (Servers) initialized for base URL: {self.base_url}")

    async def _make_request(self, method: str, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Helper method to perform API requests."""
        try:
            async with aiohttp.ClientSession() as session:
                auth = None
                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)
                async with session.request(method, url, headers=self.headers, params=params, json=data, auth=auth) as response:
                    response.raise_for_status()
                    if response.status == 204 or 'application/json' not in response.headers.get('Content-Type', ''):
                        return {"status": response.status, "message": "Success."}
                    return await response.json()
        except aiohttp.ClientError as e:
            self.logger("error", f"API request to {url} failed: {e}")
            raise


    async def get_servers(self) -> Dict:
        """
        Retrieves the list of Servers.

        Returns:
            Dict: A dictionary containing the list of servers.
        """
        url = f"{self.base_url}/v2/servers"
        self.logger("info", "Fetching list of servers")
        return await self._make_request("GET", url)

    async def get_server_config(self, server_name: str) -> Dict:
        """
        Retrieves the Server configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the server configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}"
        self.logger("info", f"Fetching configuration for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_server_config(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the Server configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            data (Dict): The new server configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}"
        self.logger("info", f"Updating configuration for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def perform_server_action(self, server_name: str, action: str, filename: Optional[str] = None) -> Dict:
        """
        Tells the Server to perform an action.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            action (str): The action to perform. Valid values: 'heapDump', 'restart', 'stackTrace', 'start', 'stop'.
            filename (Optional[str]): The file location for heap dump or stack trace.

        Returns:
            Dict: The result of the action.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/actions/{action}"
        params = {"filename": filename} if filename else None
        self.logger("info", f"Performing action '{action}' on server: {server_name}")
        return await self._make_request("PUT", url, params=params)

    async def get_server_config_adv(self, server_name: str) -> Dict:
        """
        Retrieves the advanced Server configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the advanced server configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/adv"
        self.logger("info", f"Fetching advanced configuration for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_server_config_adv(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the advanced Server configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            data (Dict): The new advanced configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/adv"
        self.logger("info", f"Updating advanced configuration for server: {server_name}")
        return await self._make_request("PUT", url, data=data)


    async def get_server_log_files(self, server_name: str, order: str = "newestFirst") -> Dict:
        """
        Retrieves the list of server log files.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            order (str): The order of files. Valid values: 'newestFirst', 'oldestFirst'. Default: 'newestFirst'.

        Returns:
            Dict: A dictionary containing the list of log files.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/logfiles"
        params = {"order": order}
        self.logger("info", f"Fetching log files for server: {server_name}")
        return await self._make_request("GET", url, params=params)

    async def get_server_log_file(self, server_name: str, log_name: str,
                                   line_count: int = 100, start_offset: Optional[int] = None,
                                   filter_str: Optional[str] = None, search: Optional[str] = None,
                                   regex_search: bool = False, head: Optional[int] = None,
                                   tail: Optional[int] = None) -> Dict:
        """
        Retrieves the contents of a Server Log with the specified log name.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            log_name (str): The name of the log file.
            line_count (int): Number of lines to retrieve. Positive for after startOffset, negative for before.
            start_offset (Optional[int]): Byte offset to start reading from.
            filter_str (Optional[str]): Predefined filters (e.g., 'noDebug|noInfo').
            search (Optional[str]): Search string or regex.
            regex_search (bool): Whether search is regex (True) or literal (False).
            head (Optional[int]): Get first x lines (overrides startOffset and lineCount).
            tail (Optional[int]): Get last x lines (overrides startOffset and lineCount).

        Returns:
            Dict: A dictionary containing the log file contents.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/logfiles/{log_name}"
        params = {"lineCount": line_count}
        if start_offset is not None:
            params["startOffset"] = start_offset
        if filter_str:
            params["filter"] = filter_str
        if search:
            params["search"] = search
        if regex_search:
            params["regexSearch"] = "true"
        if head is not None:
            params["head"] = head
        if tail is not None:
            params["tail"] = tail

        self.logger("info", f"Fetching log file '{log_name}' for server: {server_name}")
        return await self._make_request("GET", url, params=params)

    async def download_server_log_file(self, server_name: str, log_name: str) -> Dict:
        """
        Retrieves the Server Log file for the specified log name, zipped.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            log_name (str): The name of the log file.

        Returns:
            Dict: The download configuration or binary content.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/logfiles/{log_name}/download"
        self.logger("info", f"Downloading log file '{log_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_server_log_types(self, server_name: str) -> Dict:
        """
        Retrieves the list of available server Log Types.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the list of log types.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/logs"
        self.logger("info", f"Fetching log types for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_server_logs_by_type(self, server_name: str, log_type: str,
                                      line_count: int = 100, start_offset: Optional[int] = None,
                                      filter_str: Optional[str] = None, search: Optional[str] = None,
                                      regex_search: bool = False, head: Optional[int] = None,
                                      tail: Optional[int] = None, start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> Dict:
        """
        Retrieves the contents of multiple Server Logs with the specified type in the log name.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            log_type (str): The type of log (e.g., 'access', 'error').
            line_count (int): Number of lines to retrieve.
            start_offset (Optional[int]): Byte offset to start reading from.
            filter_str (Optional[str]): Predefined filters.
            search (Optional[str]): Search string or regex.
            regex_search (bool): Whether search is regex.
            head (Optional[int]): Get first x lines.
            tail (Optional[int]): Get last x lines.
            start_date (Optional[str]): Start date filter (UTC milliseconds).
            end_date (Optional[str]): End date filter (UTC milliseconds).

        Returns:
            Dict: A dictionary containing the log contents.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/logs/{log_type}"
        params = {"lineCount": line_count}
        if start_offset is not None:
            params["startOffset"] = start_offset
        if filter_str:
            params["filter"] = filter_str
        if search:
            params["search"] = search
        if regex_search:
            params["regexSearch"] = "true"
        if head is not None:
            params["head"] = head
        if tail is not None:
            params["tail"] = tail
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        self.logger("info", f"Fetching logs of type '{log_type}' for server: {server_name}")
        return await self._make_request("GET", url, params=params)


    async def get_source_driver_names(self, server_name: str) -> Dict:
        """
        Get the list of source control drivers.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the list of source control driver names.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/sourcecontrol/drivernames"
        self.logger("info", f"Fetching source control driver names for server: {server_name}")
        return await self._make_request("GET", url)
