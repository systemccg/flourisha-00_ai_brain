#!/bin/bash
#
# Validate A2A Agent Cards
# Checks that all agent cards are valid JSON and contain required fields
#
# Usage: ./validate-cards.sh

set -e

AI_BRAIN_DIR="/root/flourisha/00_AI_Brain"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${YELLOW}🔍 Validating A2A agent cards...${NC}\n"

# Find all agent cards
while IFS= read -r -d '' card_file; do
    agent_name=$(basename "$(dirname "$card_file")")
    echo -e "Checking ${YELLOW}$agent_name${NC}..."

    # Validate JSON syntax
    if ! jq empty "$card_file" 2>/dev/null; then
        echo -e "  ${RED}✗ Invalid JSON syntax${NC}"
        ((ERRORS++))
        continue
    fi

    # Check required fields
    if ! jq -e '.agent.id' "$card_file" >/dev/null 2>&1; then
        echo -e "  ${RED}✗ Missing required field: agent.id${NC}"
        ((ERRORS++))
    fi

    if ! jq -e '.agent.name' "$card_file" >/dev/null 2>&1; then
        echo -e "  ${RED}✗ Missing required field: agent.name${NC}"
        ((ERRORS++))
    fi

    if ! jq -e '.agent.description' "$card_file" >/dev/null 2>&1; then
        echo -e "  ${RED}✗ Missing required field: agent.description${NC}"
        ((ERRORS++))
    fi

    if ! jq -e '.capabilities' "$card_file" >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠ Missing recommended field: capabilities${NC}"
        ((WARNINGS++))
    fi

    if ! jq -e '.skills' "$card_file" >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠ Missing recommended field: skills${NC}"
        ((WARNINGS++))
    fi

    if [ $ERRORS -eq 0 ]; then
        echo -e "  ${GREEN}✓ Valid${NC}"
    fi
    echo
done < <(find "$AI_BRAIN_DIR/agents" -name "agent-card.json" -type f -print0)

# Summary
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All agent cards are valid!${NC}"
else
    echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $WARNINGS warning(s)${NC}"
fi

exit $ERRORS
