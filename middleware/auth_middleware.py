import os
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError


class AuthMiddleware(Middleware):
    """
    Authentication middleware for HTTP MCP requests.

    Validates that the X-Wowza-MCP-Key header matches the MCP_KEY environment variable.
    This prevents unauthorized direct connections to the MCP server.

    Note: This middleware only applies to HTTP transport mode.
    STDIO mode does not use HTTP headers.
    """

    def _validate_key(self) -> bool:
        """
        Validate the MCP key from headers against the environment variable.

        HTTP mode only - STDIO mode doesn't use this middleware.

        Returns:
            bool: True if key is valid, False otherwise
        """
        # Get the expected key from environment (server-side only)
        expected_key = os.getenv("MCP_KEY")

        # MCP_KEY must be set in HTTP mode
        if not expected_key or expected_key.strip() == "":
            raise ToolError("MCP_KEY must be set in environment for HTTP mode")

        # HTTP mode: Get and validate the key from headers
        headers = get_http_headers(include_all=True)
        headers_lower = {k.lower(): v for k, v in headers.items()}
        provided_key = headers_lower.get("x-wowza-mcp-key")

        # If no key provided in headers, authentication fails
        if not provided_key:
            return False

        # Validate the key matches
        return provided_key == expected_key

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Validate authentication before listing tools."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Validate authentication before calling any tool."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)

    async def on_list_resources(self, context: MiddlewareContext, call_next):
        """Validate authentication before listing resources."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)

    async def on_read_resource(self, context: MiddlewareContext, call_next):
        """Validate authentication before reading resources."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)

    async def on_list_prompts(self, context: MiddlewareContext, call_next):
        """Validate authentication before listing prompts."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)

    async def on_get_prompt(self, context: MiddlewareContext, call_next):
        """Validate authentication before getting a prompt."""
        if not self._validate_key():
            raise ToolError(
                "Authentication failed: Invalid or missing X-Wowza-MCP-Key header"
            )
        return await call_next(context)
