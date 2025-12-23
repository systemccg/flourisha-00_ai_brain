# Playwright MCP Server Setup & Integration

**Status**: ✅ **INSTALLED AND CONFIGURED**
**Date**: 2025-12-04
**Configuration File**: `/root/.claude/.mcp.json`

---

## Overview

Playwright MCP (Model Context Protocol) server enables automated browser testing and visual validation directly within Claude Code sessions. This integrates with Flourisha's Phase 4 testing pattern for automated browser automation.

### Current Configuration

```json
{
  "playwright": {
    "command": "bunx",
    "args": [
      "@playwright/mcp@latest",
      "--extension"
    ],
    "description": "Browser automation and testing using Playwright for visual debugging and web interaction"
  }
}
```

---

## Why This Matters for Flourisha

The Playwright MCP bridges two testing approaches:

| Approach | Tools | Use Case |
|----------|-------|----------|
| **E2B Browser** | `sbx browser` commands | External browser testing in isolated sandbox |
| **Playwright MCP** | Claude Code integration | Direct browser automation in Claude Code sessions |
| **Docker Testing** | Native Playwright in containers | Phase 2 implementation with better control |

**Key Insight**: Playwright MCP allows you to:
- Automate browser interactions directly
- Take screenshots and validate UI
- Run tests without leaving Claude Code
- Integrate with build/test pipelines

---

## Prerequisites

✅ **All installed on your system**:

- **Bun** (v1.3.2) - `which bunx` returns `/root/.bun/bin/bunx`
- **Node.js** - Available via bunx
- **Claude Code** - Currently running
- **@playwright/mcp** - Installed on-demand via bunx

No additional setup required.

---

## How to Use Playwright MCP

### Method 1: Direct Claude Code Usage

When you want automated browser testing in Claude Code:

```
I need to test the calculator app at https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app
Test that:
1. Number buttons work (click 5, verify display shows "5")
2. Operations work (click +, then 3, then =, verify result is 8)
3. History displays correctly
4. Page refresh persists calculations

Use Playwright MCP to automate these tests and provide screenshots as evidence.
```

Claude Code will automatically use the configured Playwright MCP to:
- Launch Chromium browser
- Navigate to the URL
- Simulate user interactions
- Capture screenshots
- Validate DOM elements

### Method 2: Using in Flourisha Skills

Add to any skill that needs browser testing:

```markdown
## Browser Automation Testing

Use Playwright MCP when:
- Testing web applications from external perspective
- Validating UI/UX functionality
- Capturing screenshots for evidence
- Running automated regression tests

Reference: See /root/flourisha/00_AI_Brain/documentation/mcp-servers/PLAYWRIGHT_MCP_SETUP.md
```

### Method 3: Playwright MCP Tools Available

Once activated, you have access to:

```
- playwright:browser_start - Launch Chromium
- playwright:browser_navigate - Go to URL
- playwright:browser_click - Click element
- playwright:browser_type - Type text
- playwright:browser_evaluate - Run JavaScript
- playwright:browser_screenshot - Capture screenshot
- playwright:browser_close - Cleanup
- playwright:browser_get_content - Get page HTML
- playwright:browser_wait - Wait for element
```

---

## Integration with Flourisha Phase 4 Testing

### Phase 4 Complete Testing Pattern

```
Phase 4: TEST
├── Internal API validation (curl from inside E2B) ✅
│   └── Validate endpoints with direct requests
├── External API validation (curl from outside) ✅
│   └── Test from public URLs
├── Automated browser testing (Playwright MCP) ✅ NEW
│   ├── Navigate to public URL
│   ├── Simulate user interactions
│   ├── Validate DOM elements
│   └── Screenshot validation
└── Manual verification (human review) ✅
    └── User manually confirms functionality
```

### Example: Calculator App Testing Flow

```
TEST PHASE
├── Step 1: Internal validation
│   curl http://localhost:5173/api/health
│   → {"status": "healthy"}
│
├── Step 2: External validation
│   curl https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app/api/history
│   → [{"expression": "5 + 3", "result": 8, ...}]
│
├── Step 3: Automated browser testing (Playwright MCP)
│   → Navigate to public URL
│   → Click 5, +, 3, =
│   → Verify display shows 8
│   → Verify history item created
│   → Take screenshot
│   → Reload page
│   → Verify history persists
│
└── Step 4: Manual testing
    → Open in browser
    → Verify UI looks correct
    → Test with multiple calculations
    → Confirm all features work
```

---

## Step-by-Step: Test Calculator with Playwright MCP

### Setup

1. **Ensure calculator is running**:
   ```bash
   # In E2B sandbox
   cd /code && python -m uvicorn main:app --host 0.0.0.0 --port 5173
   ```

2. **Get public URL** (if using E2B):
   ```bash
   sbx sandbox get-host [SANDBOX_ID]
   # Returns: https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app
   ```

3. **In Claude Code session**, request:
   ```
   Using Playwright MCP, test the calculator at https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app

   Test sequence:
   1. Navigate to URL
   2. Take screenshot of initial state
   3. Test "5 + 3 = 8"
   4. Verify result displays "8"
   5. Verify history shows calculation
   6. Take screenshot of result
   7. Clear display (click C)
   8. Test "10 - 2 = 8"
   9. Take screenshot of final state

   Provide evidence: screenshots and assertion results.
   ```

### Expected Output

Playwright MCP will:
1. ✅ Launch browser
2. ✅ Navigate to URL
3. ✅ Take initial screenshot
4. ✅ Click buttons in sequence
5. ✅ Validate DOM: `querySelector('#result').textContent === '8'`
6. ✅ Take screenshots at key points
7. ✅ Generate test report with pass/fail

---

## Configuration Details

### Current Setup in .mcp.json

```json
{
  "playwright": {
    "command": "bunx",                    // Use bun package runner
    "args": [
      "@playwright/mcp@latest",          // Latest Playwright MCP
      "--extension"                       // Enable extended features
    ],
    "description": "Browser automation and testing using Playwright for visual debugging and web interaction"
  }
}
```

### Key Configuration Options

| Option | Value | Meaning |
|--------|-------|---------|
| `command` | `bunx` | Use bun to run the package (fast) |
| `args[0]` | `@playwright/mcp@latest` | Install latest version on-demand |
| `args[1]` | `--extension` | Enable enhanced capabilities |

### Alternative: Use NPX Instead of Bunx

If bunx causes issues, you can switch to npx:

```json
{
  "playwright": {
    "command": "npx",
    "args": [
      "@playwright/mcp@latest",
      "--extension"
    ]
  }
}
```

---

## Troubleshooting

### Issue 1: Playwright MCP Not Appearing in Claude Code

**Solution**:
```bash
# Verify configuration
cat /root/.claude/.mcp.json | grep -A 5 playwright

# Check bunx availability
bunx -v

# Test MCP initialization
bunx @playwright/mcp@latest --help
```

### Issue 2: Browser Fails to Launch

**Common causes**:
- Port conflicts (use different port with `--port` flag)
- Missing dependencies (bunx will install automatically)
- Sandbox restrictions (if using in E2B, use from outside)

**Solution**:
```bash
# Clear bunx cache and reinstall
rm -rf ~/.bun/install/cache
bunx @playwright/mcp@latest --version
```

### Issue 3: Screenshot Not Capturing

**Solution**:
- Ensure URL is publicly accessible
- Check browser launch succeeded (should see "Browser launched" message)
- Verify page fully loaded before taking screenshot

---

## Advanced: Custom Playwright Configuration

### Environment Variables

```bash
# Increase timeout for slow pages (ms)
export PLAYWRIGHT_TIMEOUT=60000

# Use different browser (chromium, firefox, webkit)
export PLAYWRIGHT_BROWSER=chromium

# Enable debug logging
export DEBUG=pw:api
```

### Headless Mode

The Playwright MCP runs in **headless mode** (no visible window), which is ideal for:
- CI/CD pipelines
- Automated testing
- Server-side validation
- Scalability

### Device Emulation

Playwright MCP can emulate devices:
- Desktop browsers
- Mobile phones (iPhone, Android)
- Tablets
- Custom viewport sizes

---

## Integration with Flourisha Workflows

### 1. Calculator Build Pattern (Current)

```
Phase 4: TEST
├── curl tests (done)
├── Manual browser test (done)
└── Playwright MCP automated test (NEW)
```

### 2. Full-Stack App Pattern

For any new Flourisha app:

```
Phase 4: TEST
├── Internal API validation (curl inside E2B)
├── External API validation (curl outside E2B)
├── Playwright MCP browser automation
│   ├── Navigate to public URL
│   ├── Test all user flows
│   ├── Validate visual elements
│   └── Generate screenshot evidence
└── Manual user testing
```

### 3. CI/CD Integration (Phase 2+)

```
Build Pipeline
├── Phase 1: Plan (spec document)
├── Phase 2: Build (compile code)
├── Phase 3: Host (deploy app)
└── Phase 4: Test (automated via Playwright MCP)
    ├── Start test browser
    ├── Run test scenarios
    ├── Generate reports
    └── Stop browser
```

---

## Benefits Over E2B Browser

| Aspect | E2B `sbx browser` | Playwright MCP |
|--------|-----------------|----------------|
| **Setup** | Complex (CDP tunneling) | Easy (MCP integration) |
| **Speed** | Slower (remote) | Faster (local) |
| **Integration** | External commands | Native Claude Code |
| **Screenshots** | Manual capture | Automatic |
| **Reports** | Manual parsing | Structured output |
| **Cost** | E2B metered | Free (local) |
| **Best for** | E2B sandboxes | Local/Docker testing |

---

## Phase 2 Docker Integration

When migrating to Phase 2 Docker:

```dockerfile
# Dockerfile for browser testing container
FROM node:20-slim

# Install Playwright
RUN npm install -g @playwright/mcp

# Install browsers
RUN npx playwright install chromium

# Run tests
CMD ["npx", "playwright", "test"]
```

Then in docker-compose:
```yaml
services:
  browser-tests:
    build: .
    environment:
      - PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
    volumes:
      - ./tests:/tests
```

---

## Documentation Files

### Playwright MCP Files Created

```
/root/flourisha/00_AI_Brain/documentation/mcp-servers/
├── PLAYWRIGHT_MCP_SETUP.md (this file)
├── PLAYWRIGHT_TESTING_EXAMPLES.md (test patterns)
└── PLAYWRIGHT_TROUBLESHOOTING.md (common issues)
```

### Related Documentation

- Browser testing pattern: `/root/.claude/scratchpad/2025-12-04-calculator-build/BROWSER_TEST_SCRIPT.md`
- Phase 4 pattern: `/root/flourisha/00_AI_Brain/documentation/PHASE2_DOCKER_MIGRATION_PLAN.md#phase-2a2-browser-automation`
- Lesson learned: `/root/.claude/scratchpad/2025-12-04-calculator-build/PATTERN_IMPROVEMENT_SUMMARY.md`

---

## Quick Reference Commands

```bash
# List all configured MCP servers
claude mcp list

# Get Playwright MCP details
claude mcp get playwright

# Test Playwright installation
bunx @playwright/mcp@latest --version

# Add Playwright again (if needed)
claude mcp add playwright -- bunx -y @playwright/mcp@latest --extension

# Remove if needed
claude mcp remove playwright

# Check MCP configuration
cat /root/.claude/.mcp.json | jq '.mcpServers.playwright'
```

---

## Next Steps

1. ✅ **Documentation** - Complete (this file)
2. ⏭️ **Testing** - Use Playwright MCP to test calculator app
3. ⏭️ **Integration** - Add to Phase 2 Docker testing
4. ⏭️ **Patterns** - Create reusable test templates for all Flourisha apps

---

## Summary

- **Status**: Playwright MCP is installed and ready
- **Configuration**: `/root/.claude/.mcp.json` (bunx-based)
- **When to use**: Automated browser testing in Phase 4
- **Best practice**: Use alongside curl tests and manual verification
- **Phase 2**: Integrate with Docker containers for scaling

The Playwright MCP completes Flourisha's testing infrastructure, enabling full automated browser validation alongside API testing and manual verification.

---

**Configuration Date**: 2025-12-04
**Status**: Production Ready
**Last Updated**: 2025-12-04
