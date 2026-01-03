#!/bin/bash
# Frontend Tester Agent - Quick Test Runner
# Usage: ./run_tests.sh [preflight|smoke|all|feature]

set -e

FRONTEND_DIR="/root/flourisha/00_AI_Brain/frontend"
SCRIPTS_DIR="/root/flourisha/00_AI_Brain/scripts/testing"
BASE_URL="http://100.66.28.67:3000"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Frontend Tester Agent ===${NC}"
echo ""

# Step 1: Pre-flight file check
echo -e "${YELLOW}Step 1: Pre-flight file check${NC}"
REQUIRED_FILES=(
  "src/app/error.tsx"
  "src/app/global-error.tsx"
  "src/app/not-found.tsx"
  "src/app/layout.tsx"
  "src/app/page.tsx"
  ".env.local"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$FRONTEND_DIR/$file" ]; then
    echo -e "  ${GREEN}✅${NC} $file"
  else
    echo -e "  ${RED}❌ MISSING:${NC} $file"
    ALL_EXIST=false
  fi
done

if [ "$ALL_EXIST" = false ]; then
  echo -e "${RED}ERROR: Required files missing. Cannot proceed.${NC}"
  exit 1
fi
echo ""

# Step 2: Check dev server
echo -e "${YELLOW}Step 2: Checking dev server at $BASE_URL${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "  ${GREEN}✅${NC} Dev server responding (HTTP $HTTP_CODE)"
else
  echo -e "  ${RED}❌${NC} Dev server not responding (HTTP $HTTP_CODE)"
  echo -e "  Run: cd $FRONTEND_DIR && bun run dev"
  exit 1
fi
echo ""

# Step 3: Check ClickUp status
echo -e "${YELLOW}Step 3: ClickUp feature status${NC}"
if [ -f "$SCRIPTS_DIR/get_testable_features.py" ]; then
  python3 "$SCRIPTS_DIR/get_testable_features.py" --summary 2>/dev/null || echo "  (ClickUp check skipped)"
else
  echo "  (ClickUp script not found)"
fi
echo ""

# Step 4: Run tests based on argument
TEST_TYPE="${1:-preflight}"
echo -e "${YELLOW}Step 4: Running tests (type: $TEST_TYPE)${NC}"

cd "$FRONTEND_DIR"

case "$TEST_TYPE" in
  preflight)
    echo "Running pre-flight verification tests..."
    npx playwright test e2e/preflight.spec.ts --project=chromium --reporter=list
    ;;
  smoke)
    echo "Running smoke tests..."
    npx playwright test e2e/smoke.spec.ts --project=chromium --reporter=list
    ;;
  all)
    echo "Running all E2E tests..."
    npx playwright test --project=chromium --reporter=list
    ;;
  feature)
    echo "Running feature tests..."
    npx playwright test e2e/ --project=chromium --reporter=list --ignore-pattern="preflight.spec.ts"
    ;;
  *)
    echo "Unknown test type: $TEST_TYPE"
    echo "Usage: ./run_tests.sh [preflight|smoke|all|feature]"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}=== Tests completed ===${NC}"
