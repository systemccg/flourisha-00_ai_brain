# Comprehensive Frontend Test Prompt

Run a full test suite against the Flourisha frontend.

## Instructions

1. First, run pre-flight verification:
   ```bash
   /root/flourisha/00_AI_Brain/agents/frontend-tester/run_tests.sh preflight
   ```

2. Check ClickUp for completed features:
   ```bash
   python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py --summary
   ```

3. Run all E2E tests:
   ```bash
   cd /root/flourisha/00_AI_Brain/frontend
   npx playwright test --project=chromium --reporter=list
   ```

4. For any failures, investigate using Playwright MCP:
   - Navigate to the failing page
   - Take screenshots
   - Check console for errors

5. Report results in the mandatory output format with:
   - Total tests run
   - Pass/fail counts
   - ClickUp coverage percentage
   - Specific failure details

## Expected Outcome

A comprehensive test report showing:
- All pre-flight checks pass
- P1 (Core) features fully tested
- P2 (Search/Graph) features tested
- P3 (OKRs/Energy) features tested
- P4 (Settings) features marked as NOT YET IMPLEMENTED
