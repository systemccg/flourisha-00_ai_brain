#!/bin/bash
#
# Sync A2A Registry
# Regenerates registry files from current agents and skills
#
# Usage: ./sync-registry.sh [--agents] [--skills] [--all]

set -e

AI_BRAIN_DIR="/root/flourisha/00_AI_Brain"
REGISTRY_DIR="$AI_BRAIN_DIR/a2a/registry"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

sync_agents() {
    echo -e "${BLUE}📋 Syncing agent registry...${NC}"

    # Get current timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Count agents
    AGENT_COUNT=$(find "$AI_BRAIN_DIR/agents" -name "agent-card.json" -type f | wc -l)

    echo -e "${GREEN}✓ Found $AGENT_COUNT agents${NC}"
    echo -e "${YELLOW}Registry updated: $TIMESTAMP${NC}"
}

sync_skills() {
    echo -e "${BLUE}📚 Syncing skill registry...${NC}"

    # Get current timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Count skills
    SKILL_COUNT=$(find "$AI_BRAIN_DIR/skills" -name "SKILL.md" -type f | wc -l)

    echo -e "${GREEN}✓ Found $SKILL_COUNT skills${NC}"
    echo -e "${YELLOW}Registry updated: $TIMESTAMP${NC}"
}

# Parse arguments
if [ "$#" -eq 0 ] || [ "$1" == "--all" ]; then
    sync_agents
    sync_skills
elif [ "$1" == "--agents" ]; then
    sync_agents
elif [ "$1" == "--skills" ]; then
    sync_skills
else
    echo "Usage: $0 [--agents] [--skills] [--all]"
    exit 1
fi

echo -e "${GREEN}✅ Registry sync complete${NC}"
