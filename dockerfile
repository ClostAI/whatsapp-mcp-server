# syntax=docker/dockerfile:1

#################################
# 1) Build Go WhatsApp Bridge   #
#################################
FROM golang:1.24-bullseye AS bridge-builder
WORKDIR /bridge

# Install necessary build tools and SQLite development headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc \
      pkg-config \
      libsqlite3-dev \
 && rm -rf /var/lib/apt/lists/*

# Enable CGO for go-sqlite3
ENV CGO_ENABLED=1

# Copy Go module files and download dependencies
COPY whatsapp-bridge/go.mod whatsapp-bridge/go.sum ./
RUN go mod download

# Copy source code and build the binary
COPY whatsapp-bridge/ .
RUN go build -o /usr/local/bin/whatsapp-bridge main.go

#####################################
# 2) Build Python MCP Server Stage  #
#####################################
FROM python:3.12-slim AS mcp-builder
WORKDIR /app

# Install necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      gcc \
      libsqlite3-dev \
 && rm -rf /var/lib/apt/lists/*

# Set environment variable to increase pip's HTTP timeout
ENV PIP_DEFAULT_TIMEOUT=300

# Copy requirements and install dependencies using standard pip
COPY whatsapp-mcp-server/requirements.txt .
RUN python -m venv .venv \
 && .venv/bin/python -m pip install --upgrade pip setuptools wheel \
 && .venv/bin/python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY whatsapp-mcp-server/ .

#####################################
# 3) Final Runtime Image            #
#####################################
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install SQLite runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
      sqlite3 \
      libsqlite3-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy the WhatsApp bridge binary and Python application
COPY --from=bridge-builder /usr/local/bin/whatsapp-bridge /usr/local/bin/
COPY --from=mcp-builder /app /app

# Define volume for WhatsApp auth store
VOLUME ["/data/store"]

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
