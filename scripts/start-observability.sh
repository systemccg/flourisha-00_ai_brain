#!/usr/bin/env bash
#
# start-observability.sh
# Starts the Agent Observability Dashboard (server + client)
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Determine PAI_DIR
if [ -z "$PAI_DIR" ]; then
    PAI_DIR="$HOME/.claude"
    echo -e "${YELLOW}⚠️  PAI_DIR not set, using default: $PAI_DIR${NC}"
fi

OBSERVABILITY_DIR="$PAI_DIR/skills/agent-observability"
SERVER_DIR="$OBSERVABILITY_DIR/apps/server"
CLIENT_DIR="$OBSERVABILITY_DIR/apps/client"
PID_FILE="$HOME/.claude/.observability.pid"

# Check if observability system exists
if [ ! -d "$OBSERVABILITY_DIR" ]; then
    echo -e "${RED}✗ Agent observability system not found at: $OBSERVABILITY_DIR${NC}"
    echo -e "${YELLOW}Please ensure PAI is properly installed.${NC}"
    exit 1
fi

# Check if Bun is installed
if ! command -v bun &> /dev/null; then
    echo -e "${RED}✗ Bun is not installed. Please install it first:${NC}"
    echo -e "${BLUE}  curl -fsSL https://bun.sh/install | bash${NC}"
    echo -e "${BLUE}  or visit: https://bun.sh${NC}"
    exit 1
fi

# Check if already running
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE" | head -1)
    CLIENT_PID=$(cat "$PID_FILE" | tail -1)

    if ps -p "$SERVER_PID" > /dev/null 2>&1 || ps -p "$CLIENT_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Observability dashboard is already running${NC}"
        echo -e "${BLUE}  Server: http://localhost:4000${NC}"
        echo -e "${BLUE}  Client: http://localhost:5172${NC}"
        echo ""
        echo -e "To restart: ${GREEN}$PAI_DIR/scripts/restart-observability.sh${NC}"
        echo -e "To stop: ${GREEN}$PAI_DIR/scripts/stop-observability.sh${NC}"
        exit 0
    fi
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Starting Agent Observability Dashboard${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Install dependencies if needed
echo -e "${BLUE}📦 Checking dependencies...${NC}"

if [ ! -d "$SERVER_DIR/node_modules" ]; then
    echo -e "${YELLOW}  Installing server dependencies...${NC}"
    cd "$SERVER_DIR" && bun install
fi

if [ ! -d "$CLIENT_DIR/node_modules" ]; then
    echo -e "${YELLOW}  Installing client dependencies...${NC}"
    cd "$CLIENT_DIR" && bun install
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Create required directories
mkdir -p "$HOME/.claude/history/raw-outputs"
mkdir -p "$HOME/.claude/logs"

# Start server in background
echo -e "${BLUE}🔧 Starting observability server...${NC}"
cd "$SERVER_DIR"
nohup bun run dev > "$HOME/.claude/logs/observability-server.log" 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ! ps -p $SERVER_PID > /dev/null; then
    echo -e "${RED}✗ Server failed to start. Check logs:${NC}"
    echo -e "${YELLOW}  tail -f $HOME/.claude/logs/observability-server.log${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo ""

# Start client in background
echo -e "${BLUE}🎨 Starting observability client...${NC}"
cd "$CLIENT_DIR"
nohup bun run dev > "$HOME/.claude/logs/observability-client.log" 2>&1 &
CLIENT_PID=$!

# Wait a moment for client to start
sleep 3

# Check if client started successfully
if ! ps -p $CLIENT_PID > /dev/null; then
    echo -e "${RED}✗ Client failed to start. Check logs:${NC}"
    echo -e "${YELLOW}  tail -f $HOME/.claude/logs/observability-client.log${NC}"

    # Clean up server
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Client started (PID: $CLIENT_PID)${NC}"
echo ""

# Save PIDs
echo "$SERVER_PID" > "$PID_FILE"
echo "$CLIENT_PID" >> "$PID_FILE"

# Display success message
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Agent Observability Dashboard is running!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  🌐 Dashboard: ${GREEN}http://localhost:5172${NC}"
echo -e "  🔧 API Server: ${GREEN}http://localhost:4000${NC}"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  Server: ${YELLOW}tail -f $HOME/.claude/logs/observability-server.log${NC}"
echo -e "  Client: ${YELLOW}tail -f $HOME/.claude/logs/observability-client.log${NC}"
echo ""
echo -e "${BLUE}Management:${NC}"
echo -e "  Restart: ${GREEN}$PAI_DIR/scripts/restart-observability.sh${NC}"
echo -e "  Stop: ${GREEN}$PAI_DIR/scripts/stop-observability.sh${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Start using Claude Code now. The dashboard will show real-time events!${NC}"
echo ""
