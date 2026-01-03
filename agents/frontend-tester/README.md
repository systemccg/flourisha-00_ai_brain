# Frontend Tester Agent

Automated browser-based E2E testing for Flourisha frontend with ClickUp integration.

## Quick Start

```bash
# 1. Check ClickUp feature status
python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py --summary

# 2. Run pre-flight verification
cd /root/flourisha/00_AI_Brain/frontend
npx playwright test e2e/preflight.spec.ts

# 3. Run all tests
npx playwright test --project=chromium
```

## Key Principles

1. **Always test port 3000** (live server), NEVER port 3002 (Playwright managed)
2. **Check ClickUp first** - Know what features are DONE before testing
3. **Verify files exist** - error.tsx, global-error.tsx, not-found.tsx are required
4. **After git operations** - Re-verify files weren't overwritten

## Current Feature Status

| Phase | Features | Status |
|-------|----------|--------|
| P1 (Core) | Auth, layout, navigation | 15/15 |
| P2 (Search/Graph) | Search, PARA, graph | 14/15 |
| P3 (OKRs/Energy) | Dashboard widgets | 11/15 |
| P4 (Settings) | Settings, integrations | 0/15 |

## Files

| File | Purpose |
|------|---------|
| `AGENT.md` | Full agent definition and instructions |
| `run_tests.sh` | Quick test runner script |
| `prompts/` | Prompt templates for different test scenarios |

## Related Documentation

- [Testing Methodology](../../documentation/frontend/TESTING_METHODOLOGY.md)
- [Feature Route Map](../../scripts/testing/FEATURE_ROUTE_MAP.md)
- [System Spec - Frontend Testing](../../documentation/SYSTEM_SPEC.md#frontend-testing)

## ClickUp Integration

**List ID:** `901112777033` (Flourisha Frontend Dashboard)

```bash
# Get completed features as JSON
python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py

# Get markdown report
python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py --format=md

# Get summary only
python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py --summary
```

## Troubleshooting

### "Tests pass but user sees errors"
- You tested against wrong port (3002 vs 3000)
- Run: `curl -I http://100.66.28.67:3000`

### "missing required error components"
- `error.tsx` or `global-error.tsx` is missing
- Check: `ls /root/flourisha/00_AI_Brain/frontend/src/app/{error,global-error,not-found}.tsx`
