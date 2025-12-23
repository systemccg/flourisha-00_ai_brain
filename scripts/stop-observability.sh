#!/usr/bin/env bash
#
# stop-observability.sh
# Stops the Agent Observability Dashboard
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PID_FILE="$HOME/.claude/.observability.pid"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🛑 Stopping Agent Observability Dashboard${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No running dashboard found${NC}"
    echo -e "${BLUE}PID file not found: $PID_FILE${NC}"
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE" | head -1)
CLIENT_PID=$(cat "$PID_FILE" | tail -1)

STOPPED=false

# Stop server
if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo -e "${BLUE}🔧 Stopping observability server (PID: $SERVER_PID)...${NC}"
    kill "$SERVER_PID" 2>/dev/null || true
    sleep 1

    # Force kill if still running
    if ps -p "$SERVER_PID" > /dev/null 2>&1; then
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Server stopped${NC}"
    STOPPED=true
else
    echo -e "${YELLOW}⚠️  Server not running (PID: $SERVER_PID)${NC}"
fi

# Stop client
if ps -p "$CLIENT_PID" > /dev/null 2>&1; then
    echo -e "${BLUE}🎨 Stopping observability client (PID: $CLIENT_PID)...${NC}"
    kill "$CLIENT_PID" 2>/dev/null || true
    sleep 1

    # Force kill if still running
    if ps -p "$CLIENT_PID" > /dev/null 2>&1; then
        kill -9 "$CLIENT_PID" 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Client stopped${NC}"
    STOPPED=true
else
    echo -e "${YELLOW}⚠️  Client not running (PID: $CLIENT_PID)${NC}"
fi

# Remove PID file
rm -f "$PID_FILE"

echo ""
if [ "$STOPPED" = true ]; then
    echo -e "${GREEN}✅ Agent Observability Dashboard stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard was not running${NC}"
fi
echo ""
