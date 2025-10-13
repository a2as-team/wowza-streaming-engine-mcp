# wse_agent/agent.py
import os
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

AGENT_FLAGS = [os.getenv("WSE_FLAGS", "application")]

# Use cloud model
model_name = os.getenv("LLM_MODEL_CLOUD")
model = LiteLlm(model=model_name)

# Flags string for MCP
flags_str = ",".join(AGENT_FLAGS)

# MCP connection mode
mcp_mode = os.getenv("MCP_MODE", "stdio").lower()

try:
    if mcp_mode == "http":
        # -------------------------------------------------------------------
        # HTTP MODE
        # -------------------------------------------------------------------
        mcp_url = os.getenv("WSE_MCP_URL")
        if not mcp_url:
            raise ValueError("WSE_MCP_URL must be set for HTTP mode")

        # Build headers - both are required for HTTP mode
        mcp_key = os.getenv("MCP_KEY")
        if not mcp_key:
            raise ValueError("MCP_KEY must be set for HTTP mode")

        headers = {
            "X-Wowza-Flags": flags_str,
            "X-Wowza-MCP-Key": mcp_key,
        }

        connection_params = StreamableHTTPConnectionParams(
            url=mcp_url,
            headers=headers,
        )
        logger.info(f"Agent connected to MCP server via HTTP at {mcp_url} with flags: '{flags_str}'")

    else:
        # -------------------------------------------------------------------
        # STDIO MODE
        # -------------------------------------------------------------------
        # Validate that WSE_FLAGS is set for STDIO mode
        if not flags_str or flags_str.strip() == "":
            raise ValueError("WSE_FLAGS must be set for STDIO mode")

        mcp_command_str = os.getenv("MCP_COMMAND", "uv run server.py")
        command_parts = mcp_command_str.split()
        command = command_parts[0]
        args = command_parts[1:]

        subprocess_env = {
            "MCP_MODE": "stdio",
            "PYTHONUNBUFFERED": "1",
            "WOWZA_FLAGS": flags_str,  # Required for STDIO mode
        }

        # Forward engine-related env vars
        vars_to_forward = [
            "WOWZA_ENGINE_BASE_URL",
            "WOWZA_ENGINE_SERVER_NAME",
            "WOWZA_ENGINE_VHOST_NAME",
            "WOWZA_ENGINE_INSTANCE_NAME",
            "ADMIN_USER",
            "ADMIN_PASSWORD",
        ]
        for var in vars_to_forward:
            if var in os.environ:
                subprocess_env[var] = os.environ[var]

        connection_params = StdioConnectionParams(
            server_params={
                "command": command,
                "args": args,
                "env": subprocess_env,
            }
        )
        logger.info(f"Agent spawning MCP server via STDIO with command: '{mcp_command_str}' and flags: '{flags_str}'")

    # -----------------------------------------------------------------------
    # Root Agent
    # -----------------------------------------------------------------------
    root_agent = Agent(
        model=model,
        name="wse_agent",
        description="Wowza Streaming Engine agent that converts natural language prompts into Wowza REST API commands",
        instruction="""You are an expert Wowza Streaming Engine administrator. You help users manage their streaming infrastructure through natural language commands.

The available tools are filtered based on the configured flags. Use the tools you have access to for executing Wowza REST API operations.

Guidelines:
- When users request actions or data, use the appropriate tools to execute REST API calls
- Interpret natural language requests and map them to the correct tool operations
- For general Wowza questions or guidance, answer from your knowledge without tools
- Present results clearly and suggest next steps when appropriate
- If an operation fails, explain the error and suggest alternatives
- Be concise but complete in your responses""",
        tools=[MCPToolset(connection_params=connection_params)],
    )

    logger.info("Wowza Streaming Agent initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize Wowza Streaming Agent: {str(e)}", exc_info=True)
    raise


if __name__ == "__main__":
    print(f">> Wowza Agent ready in {mcp_mode.upper()} mode with flags: {flags_str}")
    while True:
        user_input = input(">> ")
        if user_input.lower() in {"exit", "quit"}:
            break
        try:
            response = root_agent.invoke(user_input)
            print(response)
        except Exception as e:
            print(f"[ERROR] {e}")
