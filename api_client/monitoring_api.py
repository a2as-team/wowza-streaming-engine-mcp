import aiohttp
import logging
from typing import Dict, Optional

class WowzaMonitoringApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for server monitoring management.
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
        self.logger("info", f"WowzaApiC (Monitoring) initialized for base URL: {self.base_url}")

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

    # --- Server Monitoring Management (v2) ---
    async def get_monitoring_config(self, server_name: str) -> Dict:
        """
        Retrieves the server monitoring configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the monitoring configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/monitoring"
        self.logger("info", f"Fetching monitoring config for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_monitoring_config(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the server monitoring configuration.

        Args:
            server_name (str): The name of the server instance.
            data (Dict): The new monitoring configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/monitoring"
        self.logger("info", f"Updating monitoring config for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def get_historic_server_stats(self, server_name: str, params: Optional[Dict] = None) -> Dict:
        """
        Retrieves the server historical statistics.

        Args:
            server_name (str): The name of the server instance.
            params (Optional[Dict]): A dictionary of query parameters to filter the results,
                                     e.g., {"startDate": "YYYY-MM-DD"}.

        Returns:
            Dict: A dictionary containing the historical server statistics.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/monitoring/historic"
        self.logger("info", f"Fetching historic server stats for: {server_name} with params: {params}")
        return await self._make_request("GET", url, params=params)


    # --- Machine Statistics (v2) ---
    async def get_current_machine_stats(self, server_name: str) -> Dict:
        """
        Retrieves current statistics for the machine.
        
        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
        
        Returns:
            Dict: A dictionary containing the current machine statistics.
        """
        if not self.base_url:
            raise ValueError("base_url is not configured")
            
        url = f"{self.base_url}/v2/machine/monitoring/current"
        self.logger("info", f"Fetching current machine statistics for server: {server_name}")
        return await self._make_request("GET", url)
    
    async def get_incoming_stream_current_stats(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        """
        Retrieves current statistics for a specific incoming stream.
        
        Args:
            server_name (str): The name of the server instance
            vhost_name (str): The virtual host name
            app_name (str): The application name
            instance_name (str): The instance name
            stream_name (str): The stream name
        
        Returns:
            Dict: A dictionary containing the current incoming stream statistics.
        """
        if not self.base_url:
            raise ValueError("base_url is not configured")
            
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/monitoring/current"
        self.logger("info", f"Fetching current incoming stream statistics for: {stream_name}")
        return await self._make_request("GET", url)

        # --- Machine Historic Statistics (v2) ---
    async def get_historic_machine_stats(self, server_name: str, params: Optional[Dict] = None) -> Dict:
        """
        Retrieves historic statistics for the machine.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            params (Optional[Dict]): A dictionary of query parameters to filter the results,
                                     e.g., {"startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD"}.

        Returns:
            Dict: A dictionary containing the historical machine statistics.
        """
        # Note: Following the consistent v2 structure `/v2/servers/{server_name}/...`
        url = f"{self.base_url}/v2/machine/monitoring/historic"
        self.logger("info", f"Fetching historic machine statistics for server: {server_name} with params: {params}")
        return await self._make_request("GET", url, params=params)