import aiohttp
import logging
from typing import Dict, Optional

class WowzaLog4jApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for server Log4j management.
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
        self.logger("info", f"WowzaApiC (Log4j) initialized for base URL: {self.base_url}")

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

    # --- Server Log4j Management (v2) ---
    async def get_log4j_config(self, server_name: str) -> Dict:
        """
        Retrieves the Server log4j configuration.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the log4j configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/log4j"
        self.logger("info", f"Fetching log4j configuration for server: {server_name}")
        return await self._make_request("GET", url)

    async def perform_global_log4j_action(self, server_name: str, action: str) -> Dict:
        """
        Tells the log4j system to perform a global action, e.g., 'reload'.

        Args:
            server_name (str): The name of the server instance.
            action (str): The action to perform (e.g., 'reload').

        Returns:
            Dict: The result of the action.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/log4j/actions/{action}"
        self.logger("info", f"Performing global log4j action '{action}' on server: {server_name}")
        return await self._make_request("PUT", url, data={})

    async def perform_logger_action(self, server_name: str, logger_name: str, action: str) -> Dict:
        """
        Tells a specified log4j logger to perform an action, such as changing its log level.

        Args:
            server_name (str): The name of the server instance.
            logger_name (str): The name of the logger to modify.
            action (str): The action to perform (e.g., 'debug', 'info', 'warn', 'error').

        Returns:
            Dict: The result of the action.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/log4j/{logger_name}/actions/{action}"
        self.logger("info", f"Performing action '{action}' on logger '{logger_name}' for server: {server_name}")
        return await self._make_request("PUT", url, data={})