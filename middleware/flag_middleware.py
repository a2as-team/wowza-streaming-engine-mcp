import os
from typing import Set

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import ToolError


def _parse_flags(raw: str | None) -> Set[str]:
    if not raw:
        return set()
    # Split by comma or space, lowercase, strip
    return {f.strip().lower() for f in raw.replace(" ", ",").split(",") if f.strip()}


class FlagMiddleware(Middleware):
    """
    Unified middleware that filters tool visibility and execution based on flags.

    Supports both HTTP and STDIO modes:
    - HTTP mode: Reads flags from X-Wowza-Flags header (REQUIRED)
    - STDIO mode: Reads flags from WOWZA_FLAGS environment variable (REQUIRED)

    If read flag is present, any tool tagged "write" is blocked.
    """

    def __init__(self, transport_mode: str = "stdio"):
        """
        Initialize the middleware with transport mode.

        Args:
            transport_mode: Either "http" or "stdio" to determine flag source
        """
        self.transport_mode = transport_mode.lower()
        if self.transport_mode not in ("http", "stdio"):
            raise ValueError(f"Invalid transport_mode: {transport_mode}. Must be 'http' or 'stdio'")

    def _get_allowed_flags(self) -> Set[str]:
        """
        Get allowed flags based on transport mode.

        Returns:
            Set of allowed flag strings

        Raises:
            ToolError: If flags are not provided or empty
        """
        if self.transport_mode == "http":
            # HTTP mode: MUST have X-Wowza-Flags header
            headers = get_http_headers(include_all=True)
            headers_lower = {k.lower(): v for k, v in headers.items()}

            header_flags = headers_lower.get("x-wowza-flags")

            if not header_flags:
                raise ToolError("X-Wowza-Flags header is required for HTTP connections")

            flags = _parse_flags(header_flags)

            if not flags:
                raise ToolError("X-Wowza-Flags header is empty - must specify at least one flag")

        else:  # stdio mode
            # STDIO mode: Read from environment variable
            env_flags = os.getenv("WOWZA_FLAGS")

            if not env_flags:
                raise ToolError("WOWZA_FLAGS must be set in environment for STDIO mode")

            flags = _parse_flags(env_flags)

            if not flags:
                raise ToolError("WOWZA_FLAGS is empty - must specify at least one flag")

        # If "all" is present, it overrides other flags, unless combined with specific access flags
        if "all" in flags:
            if "read" in flags:
                return {"all", "read"}
            if "write" in flags:
                return {"all", "write"}
            return {"all"}

        return flags

    def _tool_is_allowed(self, tool, flags: Set[str]) -> bool:
        """
        Check if a tool is allowed based on the provided flags.

        Args:
            tool: The tool object to check
            flags: Set of allowed flags

        Returns:
            True if tool is allowed, False otherwise
        """
        tool_tags: Set[str] = getattr(tool, "tags", set()) or set()

        # Handle "all"
        if "all" in flags:
            if "read" in flags:
                return "write" not in tool_tags
            elif "write" in flags:
                return "write" in tool_tags
            else:
                return True

        # Handle read mode: block write tools
        if "read" in flags and "write" in tool_tags:
            return False

        # Handle write mode: require "write" tag
        if "write" in flags:
            if "write" not in tool_tags:
                return False

        # Category filtering
        category_flags = flags - {"read", "write"}
        if not category_flags:
            # No categories → allow if not blocked above
            return True
        else:
            tool_category_tags = tool_tags - {"read", "write"}
            return bool(category_flags.intersection(tool_category_tags))


    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Filter tools list based on allowed flags."""
        tools = await call_next(context)
        flags = self._get_allowed_flags()
        filtered = [t for t in tools if self._tool_is_allowed(t, flags)]
        return filtered

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Verify tool execution is allowed based on flags."""
        flags = self._get_allowed_flags()
        try:
            if context.fastmcp_context:
                tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
                if not self._tool_is_allowed(tool, flags):
                    raise ToolError(
                        f"Access denied: tool '{context.message.name}' is not enabled for the provided flags."
                    )
        except Exception:
            # If lookup fails, let FastMCP handle unknown tool as usual
            pass

        return await call_next(context)
