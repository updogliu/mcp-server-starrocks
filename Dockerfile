FROM ghcr.io/astral-sh/uv:debian-slim

# Copy the project into the image
COPY src /app/
COPY .python-version pyproject.toml uv.lock *.md /app/

WORKDIR /app

RUN uv venv && uv pip install "mcp-server-starrocks@/app"

ENTRYPOINT ["/app/.venv/bin/mcp-server-starrocks"]
