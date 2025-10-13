import aiohttp
import logging
from typing import Dict, Optional

class WowzaListenersApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for server listener management.
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
        self.logger("info", f"WowzaApiC (Listeners) initialized for base URL: {self.base_url}")

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

    # --- Server Listener Management (v2) ---
    async def get_server_listeners(self, server_name: str) -> Dict:
        """
        Retrieves the list of server Listeners.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the server listeners configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/listeners"
        self.logger("info", f"Fetching listeners for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_server_listeners(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the server Listeners list.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').
            data (Dict): The new listeners configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/listeners"
        self.logger("info", f"Updating listeners for server: {server_name}")
        return await self._make_request("PUT", url, data=data)