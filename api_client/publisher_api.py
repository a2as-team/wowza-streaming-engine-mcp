import aiohttp
import logging
from typing import Dict, Optional

class WowzaPublisherApiClient:
    """
    Combined asynchronous API client for Wowza Streaming Engine Publisher management.

    Supports both v2 and v3 REST API endpoints:
    - v2: Basic CRUD operations (GET, POST, DELETE) - Available in builds 15089+
    - v3: Enhanced with PUT operation for updates - Available in builds 20064+

    Key differences between v2 and v3:
    - v2 uses "name" field in payload, v3 uses "publisher" field
    - v3 adds PUT method for updating existing publishers
    - Both versions support the same core functionality

    This client automatically uses the appropriate endpoint version based on
    the method called. For LLM tool usage, this provides a unified interface
    without requiring version selection.
    """

    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, logger=None):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL of the Wowza Streaming Engine server.
            username (Optional[str]): The username for authentication.
            password (Optional[str]): The password for authentication.
            logger (function, optional): A logging function.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.logger = logger if logger else lambda level, msg: logging.log(getattr(logging, level.upper(), logging.INFO), msg)
        self.logger("info", f"WowzaApiC (Publisher - Combined v2/v3) initialized for base URL: {self.base_url}")

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


    async def get_publishers(self, server_name: str) -> Dict:
        """
        Retrieves the list of server Publishers.
        Uses v3 API endpoint.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the list of publishers.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/publishers"
        self.logger("info", f"[v3] Fetching Publishers for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_publisher(self, server_name: str, publisher_name: str) -> Dict:
        """
        Retrieves the specified Publisher configuration.
        Uses v3 API endpoint.

        Args:
            server_name (str): The name of the server instance.
            publisher_name (str): The name of the publisher.

        Returns:
            Dict: A dictionary containing the specified Publisher's configuration.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v3] Fetching Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_publisher(self, server_name: str, publisher_name: str, data: Dict) -> Dict:
        """
        Adds a new Publisher to the list.
        Uses v3 API endpoint with POST to /publishers/{publisher}.

        Args:
            server_name (str): The name of the server instance.
            publisher_name (str): The name of the publisher to create.
            data (Dict): The configuration payload. Should include "publisher", "password", "description".

        Returns:
            Dict: The result of the create operation.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v3] Creating Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("POST", url, data=data)

    async def update_publisher(self, server_name: str, publisher_name: str, data: Dict) -> Dict:
        """
        Updates the specified Publisher configuration.
        Uses v3 API endpoint (v2 does not support PUT).

        Args:
            server_name (str): The name of the server instance.
            publisher_name (str): The name of the publisher to update.
            data (Dict): The configuration payload. Should include "publisher", "password", "description".

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v3] Updating Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def delete_publisher(self, server_name: str, publisher_name: str) -> Dict:
        """
        Deletes the specified Publisher configuration.
        Uses v3 API endpoint.

        Args:
            server_name (str): The name of the server instance.
            publisher_name (str): The name of the publisher to delete.

        Returns:
            Dict: The result of the delete operation.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v3] Deleting Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("DELETE", url)


    async def get_publishers_v2(self, server_name: str) -> Dict:
        """
        Retrieves the list of server Publishers using v2 API.
        Kept for backwards compatibility.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/publishers"
        self.logger("info", f"[v2] Fetching Publishers for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_publisher_v2(self, server_name: str, publisher_name: str) -> Dict:
        """
        Retrieves the specified Publisher configuration using v2 API.
        Kept for backwards compatibility.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v2] Fetching Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_publisher_v2(self, server_name: str, publisher_name: str, data: Dict) -> Dict:
        """
        Adds a new Publisher using v2 API.
        Note: v2 uses "name" field instead of "publisher" field.
        Kept for backwards compatibility.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v2] Creating Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("POST", url, data=data)

    async def delete_publisher_v2(self, server_name: str, publisher_name: str) -> Dict:
        """
        Deletes the specified Publisher using v2 API.
        Kept for backwards compatibility.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"[v2] Deleting Publisher '{publisher_name}' for server: {server_name}")
        return await self._make_request("DELETE", url)
