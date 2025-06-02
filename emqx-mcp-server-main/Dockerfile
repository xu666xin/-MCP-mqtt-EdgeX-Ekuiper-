# Dockerfile for EMQX MCP Server
# Single-stage build using Alpine-based image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Enable bytecode compilation for performance
ENV UV_COMPILE_BYTECODE=1

# Install build dependencies required for Python packages
RUN apk add --no-cache build-base libffi-dev

# Copy dependency files
COPY pyproject.toml uv.lock LICENSE README.md /app/

# Install the project's dependencies using the lockfile
# Uses cache mount to speed up builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Add the rest of the project source code and install it
COPY src /app/src

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Clean up build dependencies to reduce image size
RUN apk del build-base libffi-dev

# Set environment variable for Python path
ENV PATH="/app/.venv/bin:$PATH"

# Default command to run the EMQX MCP server
ENTRYPOINT ["emqx-mcp-server"]