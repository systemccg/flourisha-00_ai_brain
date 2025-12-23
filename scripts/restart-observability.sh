#!/usr/bin/env bash
#
# restart-observability.sh
# Restarts the Agent Observability Dashboard
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Determine PAI_DIR
if [ -z "$PAI_DIR" ]; then
    PAI_DIR="$HOME/.claude"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔄 Restarting Agent Observability Dashboard${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Stop the dashboard
if [ -f "$PAI_DIR/scripts/stop-observability.sh" ]; then
    bash "$PAI_DIR/scripts/stop-observability.sh"
else
    echo -e "${YELLOW}⚠️  Stop script not found, attempting to stop manually...${NC}"
    PID_FILE="$HOME/.claude/.observability.pid"
    if [ -f "$PID_FILE" ]; then
        SERVER_PID=$(cat "$PID_FILE" | head -1)
        CLIENT_PID=$(cat "$PID_FILE" | tail -1)
        kill "$SERVER_PID" "$CLIENT_PID" 2>/dev/null || true
        kill -9 "$SERVER_PID" "$CLIENT_PID" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
fi

echo ""
echo -e "${BLUE}Waiting 2 seconds before restart...${NC}"
sleep 2
echo ""

# Start the dashboard
if [ -f "$PAI_DIR/scripts/start-observability.sh" ]; then
    bash "$PAI_DIR/scripts/start-observability.sh"
else
    echo -e "${RED}✗ Start script not found at: $PAI_DIR/scripts/start-observability.sh${NC}"
    exit 1
fi
