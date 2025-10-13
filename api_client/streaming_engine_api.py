import aiohttp
import logging
from typing import Dict, Optional, List

class WowzaStreamingEngineApiClient:
    """
    Asynchronous API client for interacting with the Wowza Streaming Engine REST API.
    """
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, logger=None):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL of the Wowza Streaming Engine server,
                            e.g., http://localhost:8087
            logger (function, optional): A logging function. Defaults to None.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.logger = logger if logger else lambda level, msg: logging.log(getattr(logging, level.upper(), logging.INFO), msg)
        self.logger("info", f"WowzaApiC initialized for base URL: {self.base_url}")

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
                        return {"status": response.status, "message": "Success with no content returned."}
                    return await response.json()
        except aiohttp.ClientError as e:
            self.logger("error", f"API request to {url} failed: {e}")
            raise

    # --- Live Sources Management (v3) ---
    async def get_live_sources(self, server_name: str) -> Dict:
        """Get a list of live stream sources (publishers)."""
        url = f"{self.base_url}/v3/servers/{server_name}/publishers"
        self.logger("info", f"Fetching live sources for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_live_source(self, server_name: str, data: Dict) -> Dict:
        """Create a live stream source (publisher)."""
        url = f"{self.base_url}/v3/servers/{server_name}/publishers"
        self.logger("info", f"Creating live source: {data.get('publisher')}")
        return await self._make_request("POST", url, data=data)

    async def update_live_source(self, server_name: str, publisher_name: str, data: Dict) -> Dict:
        """Update a live stream source (publisher)."""
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"Updating live source: {publisher_name}")
        return await self._make_request("PUT", url, data=data)

    async def delete_live_source(self, server_name: str, publisher_name: str) -> Dict:
        """Delete a live stream source (publisher)."""
        url = f"{self.base_url}/v3/servers/{server_name}/publishers/{publisher_name}"
        self.logger("info", f"Deleting live source: {publisher_name}")
        return await self._make_request("DELETE", url)

    # --- nDVR Store Management (v2) ---
    async def get_ndvr_stores(self, server_name: str, vhost_name: str, app_name: str, instance_name: str) -> Dict:
        """Get a list of all nDVR stores for an application instance."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores"
        self.logger("info", f"Fetching nDVR store list for app: {app_name}")
        return await self._make_request("GET", url)

    async def get_ndvr_store(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, store_name: str) -> Dict:
        """Get the details of a specific nDVR store."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/{store_name}"
        self.logger("info", f"Fetching details for nDVR store: {store_name}")
        return await self._make_request("GET", url)

    async def convert_ndvr_store(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, store_name: str, conv_params: Optional[Dict] = None) -> Dict:
        """Convert a single-bitrate nDVR store to an MP4 VOD asset with optional parameters."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/{store_name}/actions/convert"
        self.logger("info", f"Initiating conversion for nDVR store: {store_name} with params: {conv_params}")
        return await self._make_request("PUT", url, params=conv_params)

    async def convert_ndvr_group(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, group_name: str, conv_params: Optional[Dict] = None) -> Dict:
        """Convert a group of ABR stream stores to MP4."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/dvrstores/actions/convert"
        self.logger("info", f"Initiating conversion for nDVR group: {group_name} with params: {conv_params}")
        return await self._make_request("PUT", url, params=conv_params)

    async def get_applications(self, server_name: str, vhost_name: str) -> Dict:
        """Get a list of all applications for a given vhost."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications"
        self.logger("info", f"Fetching applications for vhost: {vhost_name}")
        return await self._make_request("GET", url)

    # --- Stream Recorder Management (v2) ---

    async def split_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}/actions/split"
        return await self._make_request("PUT", url)

    async def stop_recorder(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, recorder_name: str) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/streamrecorders/{recorder_name}/actions/stop"
        return await self._make_request("PUT", url)

    async def get_incoming_stream_current_stats(self, server_name: str, vhost_name: str, app_name: str, instance_name: str, stream_name: str) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/instances/{instance_name}/incomingstreams/{stream_name}/monitoring/current"
        return await self._make_request("GET", url)

    # --- Stream Target (Push Publishing) Management (v2) ---
    async def get_stream_targets(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries"
        return await self._make_request("GET", url)

    async def create_stream_target(self, server_name: str, vhost_name: str, app_name: str, entry_name: str, data: dict) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("POST", url, data=data)
        
    async def delete_stream_target(self, server_name: str, vhost_name: str, app_name: str, entry_name: str) -> Dict:
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/pushpublish/mapentries/{entry_name}"
        return await self._make_request("DELETE", url)

    # --- Application Management (v2) ---
    async def create_application(self, server_name: str, vhost_name: str, app_name: str, data: dict) -> Dict:
        """Create a new application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        self.logger("info", f"Creating application: {app_name}")
        return await self._make_request("POST", url, data=data)

    async def update_application(self, server_name: str, vhost_name: str, app_name: str, data: dict) -> Dict:
        """Update an existing application's settings."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}"
        self.logger("info", f"Updating application: {app_name}")
        return await self._make_request("PUT", url, data=data)

    async def update_application_adv(self, server_name: str, vhost_name: str, app_name: str, data: dict) -> Dict:
        """Update an existing application's advanced settings (modules, properties)."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/adv"
        self.logger("info", f"Updating advanced settings for application: {app_name}")
        return await self._make_request("PUT", url, data=data)

    async def restart_application(self, server_name: str, vhost_name: str, app_name: str) -> Dict:
        """Restart a running application."""
        url = f"{self.base_url}/v2/servers/{server_name}/vhosts/{vhost_name}/applications/{app_name}/actions/restart"
        self.logger("info", f"Restarting application: {app_name}")
        # Action PUTs usually have an empty or minimal body
        return await self._make_request("PUT", url, data={})