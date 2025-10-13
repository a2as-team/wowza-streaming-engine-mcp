# syntax=docker/dockerfile:1

# Use official uv image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# Ensure the venv created by `uv sync` is preferred on PATH
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Copy project metadata first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into project environment using lockfile
RUN uv sync --frozen --no-dev

# Copy application source code
COPY . .

# Start the MCP server via uv to use the locked environment
# This CMD will be overridden by the 'command' directives in docker-compose.yml
# for both 'mcp' and 'agent' services, which is fine.
CMD ["uv", "run", "server.py"]