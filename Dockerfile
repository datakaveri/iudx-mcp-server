FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir "mcp[cli]>=1.2.0" "httpx>=0.27.0"

# Copy application code
COPY server.py .

# Transport: stdio | sse | streamable-http
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV IUDX_BASE_URL=https://v2.dev.controlplane.iudx.io

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python - <<'EOF'
import urllib.request, sys
try:
    urllib.request.urlopen("http://localhost:8000/sse", timeout=4)
    sys.exit(0)
except Exception:
    sys.exit(1)
EOF

CMD ["python", "server.py"]
