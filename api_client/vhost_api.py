import aiohttp
import logging
from typing import Dict, Optional

class WowzaVhostApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    This client is specifically tailored for VHost management.
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
        self.logger("info", f"WowzaApiC (VHost) initialized for base URL: {self.base_url}")

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

    # --- VHost Management (v2) ---
    async def get_vhosts(self, server_name: str) -> Dict:
        """Retrieves the list of VHosts."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts"
        return await self._make_request("GET", url)

    async def get_vhost(self, server_name: str, vhost_name: str) -> Dict:
        """Retrieves the specified VHost configuration."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}"
        return await self._make_request("GET", url)
        
    async def perform_vhost_action(self, server_name: str, vhost_name: str, action: str) -> Dict:
        """Performs an action (start, stop, restart) on a VHost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/actions/{action}"
        return await self._make_request("PUT", url, data={})

    # --- VHost HostPort Management (v2) ---
    async def get_hostports(self, server_name: str, vhost_name: str) -> Dict:
        """Retrieves the list of server HostPorts for the specified vhost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/hostports"
        return await self._make_request("GET", url)

    # --- VHost Statistics (v2) ---
    async def get_vhost_current_stats(self, server_name: str, vhost_name: str) -> Dict:
        """Retrieves the current VHost statistics."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/monitoring/current"
        return await self._make_request("GET", url)

    async def get_vhost_historic_stats(self, server_name: str, vhost_name: str, params: Optional[Dict] = None) -> Dict:
        """Retrieves the historic VHost statistics."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/monitoring/historic"
        return await self._make_request("GET", url, params=params)

    # --- VHost Transcoder Template Management (v2) ---
    async def get_transcoder_templates(self, server_name: str, vhost_name: str) -> Dict:
        """Retrieves the list of Transcoder Templates for the specified VHost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/transcoder/templates"
        return await self._make_request("GET", url)

    async def create_transcoder_template(self, server_name: str, vhost_name: str, template_name: str, data: Dict) -> Dict:
        """Adds a Transcoder Template to the specified VHost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/transcoder/templates/{template_name}"
        return await self._make_request("POST", url, data=data)

    async def delete_transcoder_template(self, server_name: str, vhost_name: str, template_name: str) -> Dict:
        """Deletes the specified Transcoder Template from the VHost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/transcoder/templates/{template_name}"
        return await self._make_request("DELETE", url)