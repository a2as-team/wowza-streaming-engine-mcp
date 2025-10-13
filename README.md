# Wowza Streaming MCP Server (Beta)

Seamlessly control Wowza Streaming Engine from natural-language prompts or straightforward API calls.

**Wowza Streaming MCP Server** converts high-level requests into Wowza REST commands, giving AI agents, scripts, and services instant access to the engine’s full power without boilerplate.

---

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed and running to run Docker Compose
- A [Wowza Streaming Engine](https://www.wowza.com/pricing/trial) Trial License Key

## Documentation

For more information about the Wowza Streaming Engine REST API:
- [Wowza Streaming Engine REST API Documentation](https://www.wowza.com/docs/how-to-access-documentation-for-wowza-streaming-engine-rest-api)

---

## Setup and Installation

Follow these steps to get the Wowza MCP server running locally.

### Step 1: Configure Environment Variables

Create a `.env` file in the root directory with credentials as in the `.env.example` file present in the repo.

### Step 2: Choose Your MCP Mode

The MCP server supports two connection modes:

### Option 1: STDIO Mode

In this mode, the Google ADK Client spawns the MCP server as a subprocess and communicates via stdin/stdout.

**Requirements:**
- **WOWZA_FLAGS** must be set in `.env` file (e.g., `WSE_FLAGS=application`)
- The agent passes flags to the MCP subprocess via environment variables
- No authentication required (trusted subprocess)
- **OPENAI_API_KEY** must be set in `.env` file (required for Google ADK Client UI testing)

**Start the services:**
```bash
docker compose --profile stdio up --build -d
```

**Stop the services:**
```bash
docker compose --profile stdio down
```

**Access the services:**
- **Google ADK Client UI**: http://localhost:3005/
- **Wowza Streaming Engine Manager**: http://localhost:8088/

### Option 2: HTTP Mode

In this mode, the MCP server runs as a separate HTTP service that the agent connects to. This allows external clients (like VS Code, Claude Desktop, or other MCP clients) to connect to the server.

**Requirements:**
- **MCP_KEY** MUST be set (not empty) in `.env` file for HTTP mode
- **X-Wowza-Flags** header MUST be provided in every HTTP request
- **X-Wowza-MCP-Key** header MUST be provided and match `MCP_KEY` value
- All requirements are enforced - server will reject requests that don't comply
- **OPENAI_API_KEY** must be set in `.env` file (required for Google ADK Client UI testing)

**Start the services:**
```bash
docker compose --profile http up --build -d
```

**Stop the services:**
```bash
docker compose --profile http down
```

**Access the services:**
- **Google ADK Client UI**: http://localhost:3005/
- **Wowza Streaming Engine Manager**: http://localhost:8088/
- **MCP Server (External)**: http://localhost:8002/mcp

**Connecting External Clients:**

To connect external MCP clients (like VS Code, Claude Desktop, or Windsurf) to the HTTP MCP server, add the following configuration:

Example configuration for **VS Code ** (`mcp.json`):
```json
{
  "servers": {
    "wowza-streaming-engine": {
      "url": "http://localhost:8002/mcp",
      "type": "http",
      "headers": {
        "X-Wowza-Flags": "application",
        "X-Wowza-MCP-Key": "your-secret-key-here"
      }
    }
  },
  "inputs": []
}
```

Example configuration for **Windsurf** (`mcp_config.json`):
```json
{
  "mcpServers": {
    "wowza-streaming-engine": {
      "url": "http://localhost:8002/mcp",
      "headers": {
        "X-Wowza-Flags": "application",
        "X-Wowza-MCP-Key": "your-secret-key-here"
      },
      "disabled": false,
      "disabledTools": []
    }
  }
}
```

Example configuration for **Cursor** (`mcp.json`):
```json
{
  "mcpServers": {
    "wowza-streaming-engine": {
      "url": "http://localhost:8002/mcp",
      "type": "http",
      "headers": {
        "X-Wowza-Flags": "application",
        "X-Wowza-MCP-Key": "your-secret-key-here"
      }
    }
  }
}
```

**Important Notes:**
- **X-Wowza-MCP-Key**: REQUIRED - must match the `MCP_KEY` value in your `.env` file. 
- **X-Wowza-Flags**: REQUIRED - Controls which tools are available.
  - Examples: `read`, `write`, `all`, `application`, `publisher,monitoring`
  - See [Tool Filtering with X-Wowza-Flags](#tool-filtering-with-x-wowza-flags) for details
- Both headers are strictly validated on every request. Missing or invalid headers will result in errors.

## Tool Filtering with X-Wowza-Flags

The Wowza Streaming MCP server provides granular control over which tools are exposed through the `X-Wowza-Flags` header (HTTP mode) or `WSE_FLAGS` environment variable (STDIO mode).

### Flag System Logic

The flag system works with **OR logic** for category flags and **filtering logic** for access modifiers:

**Category Flags** (combined with OR logic):
- If you specify `application,publisher`, you get ALL tools from BOTH categories
- Use specific categories to narrow down available tools

**Access Modifier Flags** (filter existing selections):
- `read`: Filters out all write/destructive operations from your selected categories
- `write`: Only shows write operations (create, update, delete) from your selected categories

### Main Category Flags

| Flag | Description |
|------|-------------|
| `application` | Application management - create, update, configure applications and instances |
| `publisher` | Publisher/live stream management - manage incoming streams and publishers |
| `transcoder` | Transcoder operations - templates, encoding, and overlay settings |
| `mediacache` | Media cache management - sources, stores, and cached assets |
| `mediacaster` | MediaCaster operations - pull streams from external sources (IP cameras, streaming servers) |
| `monitoring` | Server monitoring and statistics - performance metrics, analytics, and tuning configuration |
| `streaming_engine` | Streaming engine operations - live sources and stream targets management |
| `vhost` | Virtual host management - vHost configuration and stats |
| `server-action` | Server actions - restart, stop server operations |
| `server-config` | Server configuration - general server settings |
| `server-info` | Server information - REST API version and build details |
| `server-license` | Server license management |
| `server-listener` | Server listener configuration |
| `server-logs` | Server log management - access and read log files |
| `server-status` | Server status information |
| `user` | User management operations |
| `log4j` | Logging configuration - log levels and settings |
| `all` | All available tools |

### Access Modifier Flags

| Flag | Description |
|------|-------------|
| `read` | Filters to only read operations - removes all write/destructive capabilities |
| `write` | Filters to only write operations (create, update, delete) from selected categories |

### Read Flag Behavior

The `read` flag acts as a **filter** on your selected categories:

- `"application,read"` = All application tools BUT only read operations
- `"publisher,monitoring,read"` = All publisher AND monitoring tools BUT only read operations
- `"read"` = All tools BUT only read operations

### Flag Combination Examples

**Category OR Logic:**
```json
"X-Wowza-Flags": "application"                    // All application tools
"X-Wowza-Flags": "application,publisher"          // All application AND publisher tools
"X-Wowza-Flags": "monitoring,transcoder"          // All monitoring AND transcoder tools
```

**Read-Only Filter:**
```json
"X-Wowza-Flags": "application,read"               // All application tools, read-only
"X-Wowza-Flags": "publisher,monitoring,read"      // Publisher AND monitoring, read-only
"X-Wowza-Flags": "read"                           // All tools, read-only
```

**Write-Only Filter (create, update, delete):**
```json
"X-Wowza-Flags": "application,write"              // Only write operations for application
"X-Wowza-Flags": "publisher,write"                // Only write operations for publisher
```

**Multiple Categories:**
```json
"X-Wowza-Flags": "application,publisher,transcoder"      // All tools from these categories
"X-Wowza-Flags": "application,publisher,transcoder,read" // Same tools, but read-only
```
