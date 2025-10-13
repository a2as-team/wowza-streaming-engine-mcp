import aiohttp
import logging
from typing import Dict, Optional

class WowzaUserApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for server user management.
    """
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, logger=None):
        """
        Initializes the API client.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.logger = logger if logger else lambda level, msg: logging.log(getattr(logging, level.upper(), logging.INFO), msg)
        self.logger("info", f"WowzaApiC (User) initialized for base URL: {self.base_url}")

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

    # --- Server User Management (v2) ---
    async def get_all_users(self, server_name: str) -> Dict:
        """Retrieves the list of server Users."""
        url = f"{self.base_url}/v2/servers/{server_name}/users"
        self.logger("info", f"Fetching users for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_user(self, server_name: str, user_name: str) -> Dict:
        """Retrieves the specified User configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/users/{user_name}"
        self.logger("info", f"Fetching user '{user_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_user(self, server_name: str, user_name: str, data: Dict) -> Dict:
        """Adds the specified User configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/users/{user_name}"
        self.logger("info", f"Creating user '{user_name}' for server: {server_name}")
        return await self._make_request("POST", url, data=data)

    async def update_user(self, server_name: str, user_name: str, data: Dict) -> Dict:
        """Updates the specified User configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/users/{user_name}"
        self.logger("info", f"Updating user '{user_name}' for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def delete_user(self, server_name: str, user_name: str) -> Dict:
        """Deletes the specified User configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/users/{user_name}"
        self.logger("info", f"Deleting user '{user_name}' for server: {server_name}")
        return await self._make_request("DELETE", url)