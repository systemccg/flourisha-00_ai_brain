#!/bin/bash
# Agent Observability Dashboard Launcher
# Starts both server (port 4000) and client (port 5173)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/apps/server"
CLIENT_DIR="$SCRIPT_DIR/apps/client"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Agent Observability Dashboard Launcher${NC}"
echo ""

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo -e "${YELLOW}⚠️  Bun not found. Install with: curl -fsSL https://bun.sh/install | bash${NC}"
    exit 1
fi

# Check if dependencies are installed
echo -e "${GREEN}📦 Checking dependencies...${NC}"
if [ ! -d "$SERVER_DIR/node_modules" ]; then
    echo "Installing server dependencies..."
    cd "$SERVER_DIR" && bun install
fi

if [ ! -d "$CLIENT_DIR/node_modules" ]; then
    echo "Installing client dependencies..."
    cd "$CLIENT_DIR" && bun install
fi

echo -e "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Start server in background
echo -e "${BLUE}🚀 Starting server on port 4000...${NC}"
cd "$SERVER_DIR"
bun run dev > /tmp/observability-server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait a moment for server to start
sleep 2

# Start client in background
echo -e "${BLUE}🎨 Starting client on port 5173...${NC}"
cd "$CLIENT_DIR"
bun run dev > /tmp/observability-client.log 2>&1 &
CLIENT_PID=$!
echo "Client PID: $CLIENT_PID"

echo ""
echo -e "${GREEN}✅ Observability Dashboard Running!${NC}"
echo ""
echo "📊 Dashboard: http://localhost:5173"
echo "🔌 WebSocket: ws://localhost:4000/stream"
echo ""
echo "Server log: tail -f /tmp/observability-server.log"
echo "Client log: tail -f /tmp/observability-client.log"
echo ""
echo "To stop:"
echo "  kill $SERVER_PID $CLIENT_PID"
echo ""
echo "PIDs saved to /tmp/observability-pids.txt"
echo "$SERVER_PID" > /tmp/observability-pids.txt
echo "$CLIENT_PID" >> /tmp/observability-pids.txt

# Show server log for a few seconds
echo ""
echo -e "${BLUE}Server starting...${NC}"
sleep 3
tail -20 /tmp/observability-server.log
