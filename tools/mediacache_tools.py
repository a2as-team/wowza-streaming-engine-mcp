# tools/mediacache_tools.py
"""
MediaCache management tools for Wowza Streaming Engine.

MediaCache provides content caching from remote HTTP/S3/Azure/Google sources
to improve streaming performance and reduce bandwidth costs.

Combined v2/v3 support:
- Standard operations use v3 API (better field names: sourceName/storeName)
- Advanced main config uses v2 API (only version with /adv endpoint)
- No version parameter needed - client handles it automatically
"""

import json
import logging
from typing import Dict, Optional, Union, Literal

from api_client.mediacache_api import WowzaMediaCacheApiClient
from models import (
    MediaCacheSourceCreate,
    MediaCacheStoreCreate,
    MediaCacheConfigUpdate,
)
from .shared_client_utils import get_engine_config, make_client


def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine Media Cache MCP tools.
    """
    client = make_client(WowzaMediaCacheApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"mediacache", "read"},
        description="Retrieve MediaCache configuration. Use 'advanced' flag to get advanced settings."
    )
    async def get_wowza_media_cache_config(
        advanced: bool = False
    ) -> str:
        """
        Retrieve MediaCache configuration including sources, stores, and settings.

        Args:
            advanced: If False (default), returns standard configuration including
                     sources, stores, thread pool settings. If True, returns advanced
                     configuration settings (uses v2 API internally).

        Returns:
            JSON string containing the MediaCache configuration.

        Examples:
            # Get standard config
            get_wowza_media_cache_config()

            # Get advanced config
            get_wowza_media_cache_config(advanced=True)
        """
        if advanced:
            result = await client.get_media_cache_adv_config(server_name=config["server_name"])
        else:
            result = await client.get_media_cache_config(server_name=config["server_name"])

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"mediacache", "write"},
        description="Update MediaCache configuration settings. Use 'advanced' flag for advanced settings."
    )
    async def update_wowza_media_cache_config(
        config_data: Union[Dict, MediaCacheConfigUpdate],
        advanced: bool = False
    ) -> str:
        """
        Update MediaCache configuration.

        Args:
            config_data: Configuration data as Dict or MediaCacheConfigUpdate model.
            advanced: If False (default), updates standard configuration.
                     If True, updates advanced configuration (uses v2 API internally).

        Returns:
            JSON string confirming the update with status information.

        Examples:
            # Update standard config
            update_wowza_media_cache_config(config_data={...})

            # Update advanced config
            update_wowza_media_cache_config(config_data={...}, advanced=True)
        """
        if isinstance(config_data, MediaCacheConfigUpdate):
            payload = config_data.model_dump(exclude_none=True)
        else:
            payload = config_data

        if advanced:
            result = await client.update_media_cache_adv_config(
                server_name=config["server_name"],
                data=payload
            )
        else:
            result = await client.update_media_cache_config(
                server_name=config["server_name"],
                data=payload
            )

        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"mediacache", "read"},
        description="Get MediaCache sources. If no source_name provided, returns all sources. If source_name provided, returns specific source."
    )
    async def get_wowza_media_cache_source(
        source_name: Optional[str] = None
    ) -> str:
        """
        Get MediaCache sources.

        Sources define where content is fetched from (HTTP, S3, Azure, Google Cloud).

        Args:
            source_name: Optional source name.
                - If None: Returns list of all sources
                - If provided: Returns specific source configuration

        Returns:
            JSON string containing source(s) configuration.

        Examples:
            # List all sources
            get_wowza_media_cache_source()

            # Get specific source
            get_wowza_media_cache_source("my-s3-source")
        """
        if source_name:
            result = await client.get_media_cache_source(
                server_name=config["server_name"],
                source_name=source_name
            )
        else:
            result = await client.get_media_cache_sources(server_name=config["server_name"])

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"mediacache", "write"},
        description="Manage MediaCache source operations: create, update, or delete sources. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_media_cache_source(
        operation: Literal["create", "update", "delete"],
        source_name: str,
        source_data: Optional[Union[Dict, MediaCacheSourceCreate]] = None
    ) -> str:
        """
        Manage MediaCache source operations (create, update, delete).

        Sources define remote locations where content is fetched from.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            operation: The operation to perform:
                - "create": Create new source (source_data optional - uses HTTP defaults if None)
                - "update": Update existing source (requires source_data)
                - "delete": Delete source (only needs source_name)
            source_name: Name of the source.
            source_data: Source configuration (required for update, optional for create).
                        For create with None, auto-generates default HTTP source.

        Returns:
            JSON string confirming the operation.

        Raises:
            ValueError: If required parameters are missing for the operation.

        Examples:
            # Create with auto-generated defaults (HTTP source)
            manage_wowza_media_cache_source(
                operation="create",
                source_name="my-http-source"
            )

            # Create with custom config
            manage_wowza_media_cache_source(
                operation="create",
                source_name="my-s3-source",
                source_data={
                    "type": "S3",
                    "basePath": "s3://my-bucket",
                    "awsAccessKeyId": "...",
                    "awsSecretAccessKey": "...",
                    ...
                }
            )

            # Update source
            manage_wowza_media_cache_source(
                operation="update",
                source_name="my-s3-source",
                source_data={...}
            )

            # Delete source
            manage_wowza_media_cache_source(
                operation="delete",
                source_name="my-s3-source"
            )
        """
        if operation == "create":
            if source_data is None:
                default_payload = {
                    "version": "3",
                    "serverName": config["server_name"],
                    "description": f"Auto-generated MediaCache source {source_name}",
                    "sourceName": source_name,
                    "type": "HTTP",
                    "basePath": "http://",
                    "prefix": f"{source_name}/",
                    "minTimeToLive": 600000,
                    "maxTimeToLive": 1200000,
                    "isAmazonS3": False,
                    "s3BucketNameInDomain": False,
                    "awsAccessKeyId": "",
                    "awsSecretAccessKey": "",
                    "isPassThru": False,
                    "baseClass": "com.wowza.wms.mediacache.impl.MediaCacheItemHTTPImpl",
                    "readerClass": "",
                    "httpReaderFactoryClass": "",
                    "azureAccountName": "",
                    "azureContainerName": "",
                    "azureAccountKey": "",
                    "googleServiceID": "",
                    "googleServiceKey": "",
                    "googleServicePrivateKeyFile": "",
                    "googleServicePrivateKeyPassword": "",
                    "googleEncMethod": ""
                }
                payload = default_payload
            elif isinstance(source_data, MediaCacheSourceCreate):
                payload = source_data.model_dump(exclude_none=True)
            else:
                payload = source_data

            result = await client.create_media_cache_source(
                server_name=config["server_name"],
                source_name=source_name,
                data=payload
            )

        elif operation == "update":
            if source_data is None:
                raise ValueError("'source_data' is required for update operation")

            if isinstance(source_data, MediaCacheSourceCreate):
                payload = source_data.model_dump(exclude_none=True)
            else:
                payload = source_data

            result = await client.update_media_cache_source(
                server_name=config["server_name"],
                source_name=source_name,
                data=payload
            )

        elif operation == "delete":
            result = await client.delete_media_cache_source(
                server_name=config["server_name"],
                source_name=source_name
            )

        else:
            raise ValueError(f"Invalid operation: {operation}. Must be 'create', 'update', or 'delete'")

        return json.dumps(result, indent=2)


    @mcp.tool(
        tags={"mediacache", "read"},
        description="Get MediaCache stores. If no store_name provided, returns all stores. If store_name provided, returns specific store."
    )
    async def get_wowza_media_cache_store(
        store_name: Optional[str] = None
    ) -> str:
        """
        Get MediaCache stores.

        Stores define local disk locations where cached content is stored.

        Args:
            store_name: Optional store name.
                - If None: Returns list of all stores
                - If provided: Returns specific store configuration

        Returns:
            JSON string containing store(s) configuration.

        Examples:
            # List all stores
            get_wowza_media_cache_store()

            # Get specific store
            get_wowza_media_cache_store("default")
        """
        if store_name:
            result = await client.get_media_cache_store(
                server_name=config["server_name"],
                store_name=store_name
            )
        else:
            result = await client.get_media_cache_stores(server_name=config["server_name"])

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"mediacache", "write"},
        description="Manage MediaCache store operations: create, update, or delete stores. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_media_cache_store(
        operation: Literal["create", "update", "delete"],
        store_name: str,
        store_data: Optional[Union[Dict, MediaCacheStoreCreate]] = None
    ) -> str:
        """
        Manage MediaCache store operations (create, update, delete).

        Stores define local disk locations for cached content.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            operation: The operation to perform:
                - "create": Create new store (store_data optional - uses defaults if None)
                - "update": Update existing store (requires store_data)
                - "delete": Delete store (only needs store_name)
            store_name: Name of the store.
            store_data: Store configuration (required for update, optional for create).
                       For create with None, auto-generates default store settings.

        Returns:
            JSON string confirming the operation.

        Raises:
            ValueError: If required parameters are missing for the operation.

        Examples:
            # Create with auto-generated defaults
            manage_wowza_media_cache_store(
                operation="create",
                store_name="fast-ssd-store"
            )

            # Create with custom config
            manage_wowza_media_cache_store(
                operation="create",
                store_name="large-store",
                store_data={
                    "path": "/mnt/cache",
                    "maxSize": "100G",
                    "writeRate": "32M",
                    ...
                }
            )

            # Update store
            manage_wowza_media_cache_store(
                operation="update",
                store_name="large-store",
                store_data={...}
            )

            # Delete store
            manage_wowza_media_cache_store(
                operation="delete",
                store_name="large-store"
            )
        """
        if operation == "create":
            if store_data is None:
                default_config = {
                    "version": "3",
                    "serverName": config["server_name"],
                    "storeName": store_name,
                    "description": f"MediaCache store {store_name}",
                    "path": "${com.wowza.wms.context.ServerConfigHome}/mediacache",
                    "maxSize": "10G",
                    "writeRate": "16M",
                    "writeRateMaxBucketSize": "64M",
                }
                payload = default_config
            elif isinstance(store_data, MediaCacheStoreCreate):
                payload = store_data.model_dump(exclude_none=True)
            else:
                payload = store_data

            result = await client.create_media_cache_store(
                server_name=config["server_name"],
                store_name=store_name,
                data=payload
            )

        elif operation == "update":
            if store_data is None:
                raise ValueError("'store_data' is required for update operation")

            if isinstance(store_data, MediaCacheStoreCreate):
                payload = store_data.model_dump(exclude_none=True)
            else:
                payload = store_data

            result = await client.update_media_cache_store(
                server_name=config["server_name"],
                store_name=store_name,
                data=payload
            )

        elif operation == "delete":
            result = await client.delete_media_cache_store(
                server_name=config["server_name"],
                store_name=store_name
            )

        else:
            raise ValueError(f"Invalid operation: {operation}. Must be 'create', 'update', or 'delete'")

        return json.dumps(result, indent=2)
