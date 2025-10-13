# tools/publisher_tools.py
"""
Publisher management tools for Wowza Streaming Engine.

Publishers are used to authenticate incoming RTMP and RTSP streams.

Combined v2/v3 support:
- All operations use v3 API by default (more features, better field names)
- v2 API methods available internally for backwards compatibility
- Update operation only available in v3 (not in v2)
"""

import json
import logging
from typing import Dict, Optional, Literal

from api_client.publisher_api import WowzaPublisherApiClient
from .shared_client_utils import get_engine_config, make_client


def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine Publisher-related MCP tools.
    """
    client = make_client(WowzaPublisherApiClient, CONFIG)
    config = get_engine_config(CONFIG)


    @mcp.tool(
        tags={"publisher", "read"},
        description="Retrieves Publisher configurations. If no publisher_name provided, returns all publishers. If publisher_name provided, returns specific publisher details."
    )
    async def get_wowza_publisher(
        publisher_name: Optional[str] = None
    ) -> str:
        """
        Retrieves Publisher configurations for authenticating incoming streams.

        Publishers are used to authenticate incoming RTMP and RTSP streams.
        Each publisher has a username (publisher name) and password.

        Args:
            publisher_name: Optional publisher name.
                - If None: Returns list of all publishers
                - If provided: Returns specific publisher's full configuration

        Returns:
            JSON string containing publisher(s) configuration including
            password, description, and other settings.

        Examples:
            # List all publishers
            get_wowza_publisher()

            # Get specific publisher
            get_wowza_publisher("broadcaster1")
        """
        if publisher_name is None:
            # List all publishers
            result = await client.get_publishers(
                server_name=config["server_name"]
            )
        else:
            # Get specific publisher
            result = await client.get_publisher(
                server_name=config["server_name"],
                publisher_name=publisher_name
            )

        return json.dumps(result, indent=2)

    @mcp.tool(
        tags={"publisher", "write"},
        description="Manages Publisher operations: create, update, or delete publishers for stream authentication. WARNING: For delete operations, ALWAYS confirm with user before executing."
    )
    async def manage_wowza_publisher(
        operation: Literal["create", "update", "delete"],
        publisher_name: str,
        password: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Manages Publisher operations (create, update, delete).

        Publishers control who can push streams to the server via RTMP or RTSP.

        WARNING: When using 'delete' operation, this is a DESTRUCTIVE operation that removes stream authentication.
        ALWAYS confirm with the user before executing delete operations.

        Args:
            operation: The operation to perform:
                - "create": Create new publisher (requires password)
                - "update": Update existing publisher password/description (v3 only)
                - "delete": Delete publisher
            publisher_name: The username/name of the publisher.
            password: Password for authentication.
                - Required for "create"
                - Optional for "update" (provide if changing password)
                - Ignored for "delete"
            description: Optional description for administrative purposes.
                - Optional for "create" and "update"
                - Ignored for "delete"

        Returns:
            JSON string confirming the operation with status information.

        Raises:
            ValueError: If required parameters are missing for the operation.

        Examples:
            # Create new publisher
            manage_wowza_publisher(
                operation="create",
                publisher_name="broadcaster1",
                password="SecurePass123",
                description="Main event broadcaster"
            )

            # Update password only
            manage_wowza_publisher(
                operation="update",
                publisher_name="broadcaster1",
                password="NewSecurePass456"
            )

            # Update description only
            manage_wowza_publisher(
                operation="update",
                publisher_name="broadcaster1",
                description="Updated description"
            )

            # Delete publisher
            manage_wowza_publisher(
                operation="delete",
                publisher_name="broadcaster1"
            )
        """
        if operation == "create":
            # CREATE operation - requires password
            if not password:
                raise ValueError("'password' is required for create operation")

            payload = {
                "version": "3",
                "serverName": config["server_name"],
                "publisher": publisher_name,
                "password": password,
                "description": description or f"Publisher {publisher_name}"
            }

            result = await client.create_publisher(
                server_name=config["server_name"],
                publisher_name=publisher_name,
                data=payload
            )

        elif operation == "update":
            # UPDATE operation - requires at least password or description
            if password is None and description is None:
                raise ValueError("At least one of 'password' or 'description' must be provided for update operation")

            payload = {
                "version": "3",
                "serverName": config["server_name"],
                "publisher": publisher_name,
            }

            if password is not None:
                payload["password"] = password
            if description is not None:
                payload["description"] = description

            result = await client.update_publisher(
                server_name=config["server_name"],
                publisher_name=publisher_name,
                data=payload
            )

        elif operation == "delete":
            # DELETE operation - only needs publisher_name
            result = await client.delete_publisher(
                server_name=config["server_name"],
                publisher_name=publisher_name
            )

        else:
            raise ValueError(f"Invalid operation: {operation}. Must be 'create', 'update', or 'delete'")

        return json.dumps(result, indent=2)
