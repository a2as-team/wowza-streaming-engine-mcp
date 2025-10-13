import aiohttp
import logging
from typing import Dict, Optional

class WowzaMediaCacheApiClient:
    """
    Combined asynchronous API client for Wowza Streaming Engine MediaCache management.

    Supports both v2 and v3 REST API endpoints:
    - v2: Includes /adv endpoint for advanced main config - Available in builds 15089+
    - v3: Standard config, sources, stores with field name updates - Available in builds 15089+

    Key differences between v2 and v3:
    - v2 uses "name" field in source/store payloads, v3 uses "sourceName"/"storeName"
    - v2 has /mediacache/adv endpoint (GET/PUT/POST) for advanced settings
    - v3 does NOT have /mediacache/adv endpoint (missing from API)
    - v3 has /mediacache/sources/{source}/adv and /mediacache/stores/{store}/adv

    This client provides a unified interface:
    - Main methods use v3 for standard operations (better field names)
    - Advanced main config methods use v2 (only version with this endpoint)
    - Automatically handles version selection internally
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
        self.logger("info", f"WowzaApiC (MediaCache - Combined v2/v3) initialized for base URL: {self.base_url}")

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


    async def get_media_cache_config(self, server_name: str) -> Dict:
        """
        Retrieves the server MediaCache configuration.
        Uses v3 API endpoint.

        Args:
            server_name (str): The name of the server instance (e.g., '_defaultServer_').

        Returns:
            Dict: A dictionary containing the MediaCache configuration.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache"
        self.logger("info", f"[v3] Fetching MediaCache config for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_media_cache_config(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the server MediaCache configuration.
        Uses v3 API endpoint.

        Args:
            server_name (str): The name of the server instance.
            data (Dict): The MediaCache configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache"
        self.logger("info", f"[v3] Updating MediaCache config for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def get_media_cache_adv_config(self, server_name: str) -> Dict:
        """
        Retrieves the advanced MediaCache configuration.
        Uses v2 API endpoint (v3 does NOT have this endpoint).

        Args:
            server_name (str): The name of the server instance.

        Returns:
            Dict: A dictionary containing the advanced MediaCache configuration.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/mediacache/adv"
        self.logger("info", f"[v2] Fetching advanced MediaCache config for server: {server_name}")
        return await self._make_request("GET", url)

    async def update_media_cache_adv_config(self, server_name: str, data: Dict) -> Dict:
        """
        Updates the advanced MediaCache configuration.
        Uses v2 API endpoint (v3 does NOT have this endpoint).

        Args:
            server_name (str): The name of the server instance.
            data (Dict): The advanced configuration payload.

        Returns:
            Dict: The result of the update operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/mediacache/adv"
        self.logger("info", f"[v2] Updating advanced MediaCache config for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def create_media_cache_adv_config(self, server_name: str, data: Dict) -> Dict:
        """
        Creates advanced MediaCache configuration.
        Uses v2 API endpoint (v3 does NOT have this endpoint).

        Args:
            server_name (str): The name of the server instance.
            data (Dict): The advanced configuration payload.

        Returns:
            Dict: The result of the create operation.
        """
        url = f"{self.base_url}/v2/servers/{server_name}/mediacache/adv"
        self.logger("info", f"[v2] Creating advanced MediaCache config for server: {server_name}")
        return await self._make_request("POST", url, data=data)


    async def get_media_cache_sources(self, server_name: str) -> Dict:
        """
        Retrieves the list of MediaCache Sources.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources"
        self.logger("info", f"[v3] Fetching MediaCache sources for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_media_cache_source(self, server_name: str, source_name: str) -> Dict:
        """
        Retrieves the specified MediaCache Source configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}"
        self.logger("info", f"[v3] Fetching MediaCache source '{source_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_media_cache_source(self, server_name: str, source_name: str, data: Dict) -> Dict:
        """
        Adds or creates the specified MediaCache Source configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}"
        self.logger("info", f"[v3] Creating MediaCache source '{source_name}' for server: {server_name}")
        return await self._make_request("POST", url, data=data)

    async def update_media_cache_source(self, server_name: str, source_name: str, data: Dict) -> Dict:
        """
        Updates the specified MediaCache Source configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}"
        self.logger("info", f"[v3] Updating MediaCache source '{source_name}' for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def delete_media_cache_source(self, server_name: str, source_name: str) -> Dict:
        """
        Deletes the specified MediaCache Source configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}"
        self.logger("info", f"[v3] Deleting MediaCache source '{source_name}' for server: {server_name}")
        return await self._make_request("DELETE", url)

    async def get_media_cache_source_adv(self, server_name: str, source_name: str) -> Dict:
        """
        Retrieves the advanced configuration for a specific MediaCache Source.
        Uses v3 API endpoint (v2 also has this but v3 has better field names).
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}/adv"
        self.logger("info", f"[v3] Fetching advanced config for source '{source_name}' on server: {server_name}")
        return await self._make_request("GET", url)

    async def update_media_cache_source_adv(self, server_name: str, source_name: str, data: Dict) -> Dict:
        """
        Updates the advanced configuration for a specific MediaCache Source.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}/adv"
        self.logger("info", f"[v3] Updating advanced config for source '{source_name}' on server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def create_media_cache_source_adv(self, server_name: str, source_name: str, data: Dict) -> Dict:
        """
        Creates advanced configuration for a specific MediaCache Source.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/sources/{source_name}/adv"
        self.logger("info", f"[v3] Creating advanced config for source '{source_name}' on server: {server_name}")
        return await self._make_request("POST", url, data=data)


    async def get_media_cache_stores(self, server_name: str) -> Dict:
        """
        Retrieves the list of MediaCache Stores.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores"
        self.logger("info", f"[v3] Fetching MediaCache stores for server: {server_name}")
        return await self._make_request("GET", url)

    async def get_media_cache_store(self, server_name: str, store_name: str) -> Dict:
        """
        Retrieves the specified MediaCache Store configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}"
        self.logger("info", f"[v3] Fetching MediaCache store '{store_name}' for server: {server_name}")
        return await self._make_request("GET", url)

    async def create_media_cache_store(self, server_name: str, store_name: str, data: Dict) -> Dict:
        """
        Adds or creates the specified MediaCache Store configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}"
        self.logger("info", f"[v3] Creating MediaCache store '{store_name}' for server: {server_name}")
        return await self._make_request("POST", url, data=data)

    async def update_media_cache_store(self, server_name: str, store_name: str, data: Dict) -> Dict:
        """
        Updates the specified MediaCache Store configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}"
        self.logger("info", f"[v3] Updating MediaCache store '{store_name}' for server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def delete_media_cache_store(self, server_name: str, store_name: str) -> Dict:
        """
        Deletes the specified MediaCache Store configuration.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}"
        self.logger("info", f"[v3] Deleting MediaCache store '{store_name}' for server: {server_name}")
        return await self._make_request("DELETE", url)

    async def get_media_cache_store_adv(self, server_name: str, store_name: str) -> Dict:
        """
        Retrieves the advanced configuration for a specific MediaCache Store.
        Uses v3 API endpoint (v2 also has this but v3 has better field names).
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}/adv"
        self.logger("info", f"[v3] Fetching advanced config for store '{store_name}' on server: {server_name}")
        return await self._make_request("GET", url)

    async def update_media_cache_store_adv(self, server_name: str, store_name: str, data: Dict) -> Dict:
        """
        Updates the advanced configuration for a specific MediaCache Store.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}/adv"
        self.logger("info", f"[v3] Updating advanced config for store '{store_name}' on server: {server_name}")
        return await self._make_request("PUT", url, data=data)

    async def create_media_cache_store_adv(self, server_name: str, store_name: str, data: Dict) -> Dict:
        """
        Creates advanced configuration for a specific MediaCache Store.
        Uses v3 API endpoint.
        """
        url = f"{self.base_url}/v3/servers/{server_name}/mediacache/stores/{store_name}/adv"
        self.logger("info", f"[v3] Creating advanced config for store '{store_name}' on server: {server_name}")
        return await self._make_request("POST", url, data=data)
