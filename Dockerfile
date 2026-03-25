FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir "mcp[cli]>=1.2.0" "httpx>=0.27.0"

# Copy application code
COPY server.py .
COPY tools/ tools/

# Transport: stdio | sse | streamable-http
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV IUDX_BASE_URL=https://mahaagx.maharashtra.gov.in/controlplane/
ENV RS_BASE_URL=https://mahaagx.maharashtra.gov.in/dataplane/
ENV RSP_BASE_URL=https://mahaagx.maharashtra.gov.in/dataplane/rsp/
ENV FILES_BASE_URL=https://mahaagx.maharashtra.gov.in/files-connect-api/v1/
ENV ES_INDEX_PREFIX=""

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import http.client, sys; c=http.client.HTTPConnection('localhost',8000,timeout=4); c.request('GET','/sse'); r=c.getresponse(); sys.exit(0 if r.status==200 else 1)"

CMD ["python", "server.py"]
