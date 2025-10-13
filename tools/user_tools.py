import json
import logging
from typing import Dict, Optional, List, Literal

from api_client.user_api import WowzaUserApiClient
from models import UserCreate, UserUpdate
from models.schema_utils import create_enhanced_tool_description
from .shared_client_utils import get_engine_config, make_client

def register_tools(mcp, CONFIG=None):
    """
    Register Wowza Streaming Engine server user-related MCP tools.

    SECURITY NOTE: User management tools are commented out by default.
    Uncomment only in secure, controlled environments.
    """
    client = make_client(WowzaUserApiClient, CONFIG)
    config = get_engine_config(CONFIG)

    @mcp.tool(
        tags={"user", "read"},
        description="Retrieves user information. If no user_name provided, returns all users."
    )
    async def get_wowza_user(
        user_name: Optional[str] = None
    ) -> str:
        """
        Retrieves user configuration (read-only, safe operation).

        Args:
            user_name: Optional user name. If None, returns all users.
        """
        if user_name is None:
            result = await client.get_all_users(server_name=config["server_name"])
        else:
            result = await client.get_user(
                server_name=config["server_name"],
                user_name=user_name
            )
        return json.dumps(result, indent=2)

    # ============================================================================
    # SECURITY-SENSITIVE TOOLS - COMMENTED OUT BY DEFAULT
    # ============================================================================
    # The following tools can create, modify, or delete users and passwords.
    # Only enable these in secure, controlled environments with proper access control.
    # ============================================================================

    # @mcp.tool(
    #     tags={"user", "write", "security-sensitive"},
    #     description=create_enhanced_tool_description(
    #         "Create a new Wowza user. SECURITY WARNING: Handles authentication credentials.",
    #         UserCreate,
    #         "user_data"
    #     )
    # )
    # async def create_wowza_user(
    #     user_data: UserCreate
    # ) -> str:
    #     """
    #     Creates a new user in Wowza Streaming Engine.
    #
    #     SECURITY WARNING: This tool creates user accounts with passwords.
    #     Only use in secure, controlled environments.
    #
    #     Args:
    #         user_data: User configuration including userName (required), password (required),
    #                    and optional description, groups, passwordEncoding, realm.
    #     """
    #     payload = user_data.model_dump(exclude_none=True)
    #     result = await client.create_user(
    #         server_name=config["server_name"],
    #         user_name=user_data.userName,
    #         data=payload
    #     )
    #     return json.dumps(result, indent=2)

    # @mcp.tool(
    #     tags={"user", "write", "security-sensitive"},
    #     description=create_enhanced_tool_description(
    #         "Update user settings (password, groups, etc). SECURITY WARNING: Can change passwords.",
    #         UserUpdate,
    #         "user_data"
    #     )
    # )
    # async def update_wowza_user(
    #     user_name: str,
    #     user_data: UserUpdate
    # ) -> str:
    #     """
    #     Updates an existing user's configuration.
    #
    #     SECURITY WARNING: This tool can change user passwords and group memberships.
    #     Only use in secure, controlled environments.
    #
    #     Args:
    #         user_name: The username to update
    #         user_data: Updated user configuration (all fields optional)
    #     """
    #     # Get current config
    #     current_config = await client.get_user(
    #         server_name=config["server_name"],
    #         user_name=user_name
    #     )
    #
    #     # Merge with updates
    #     update_dict = user_data.model_dump(exclude_none=True)
    #     current_config.update(update_dict)
    #
    #     result = await client.update_user(
    #         server_name=config["server_name"],
    #         user_name=user_name,
    #         data=current_config
    #     )
    #     return json.dumps(result, indent=2)

    # @mcp.tool(
    #     tags={"user", "write", "security-sensitive"},
    #     description="Delete a user from Wowza. SECURITY WARNING: Permanently removes user access."
    # )
    # async def delete_wowza_user(
    #     user_name: str
    # ) -> str:
    #     """
    #     Deletes a user from Wowza Streaming Engine.
    #
    #     SECURITY WARNING: This permanently removes user access.
    #     Only use in secure, controlled environments.
    #
    #     Args:
    #         user_name: The username to delete
    #     """
    #     result = await client.delete_user(
    #         server_name=config["server_name"],
    #         user_name=user_name
    #     )
    #     return json.dumps(result, indent=2)
