# Calculator Browser Automation Test Script

**Status**: Created (E2B browser limitations prevent execution)
**Purpose**: Demonstrate proper Phase 4 automated browser testing pattern
**Tool**: E2B's `sbx browser` (Playwright-based)

---

## Intended Test Flow

This is the **proper automated test pattern** that should be executed:

### Step 1: Initialize Browser
```bash
source ~/.local/bin/env
export E2B_API_KEY="e2b_4f555888358be28ebfb1d67f81dc99b471d75148"
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/

# One-time setup
uv run sbx browser init
```

**Expected Output**: Playwright and Chromium installed

---

### Step 2: Start Browser Service
```bash
uv run sbx browser start --port 9223
```

**Expected Output**: Browser listening on port 9223

---

### Step 3: Navigate to Calculator
```bash
uv run sbx browser nav https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app
```

**Expected Output**: Page loads successfully

---

### Step 4: Take Initial Screenshot
```bash
uv run sbx browser screenshot
```

**Expected Output**: Screenshot shows calculator UI with:
- Display showing "0"
- 4x5 button grid
- History panel
- Modern dark theme

---

### Step 5: Test Calculation Flow - "5 + 3 = ?"

```bash
# Click number 5
uv run sbx browser click "button:nth-of-type(9)"

# Verify display shows "5"
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "5"

# Click operator +
uv run sbx browser click "button:contains('+')"

# Verify display shows "5 +"
uv run sbx browser eval "document.getElementById('expression').textContent"
# Expected: "5 +"

# Click number 3
uv run sbx browser click "button:nth-of-type(11)"

# Verify display shows "5 + 3"
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "5 + 3"

# Click equals
uv run sbx browser click "button:contains('=')"

# Wait for response
sleep 2

# Verify result is 8
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "8"
```

---

### Step 6: Test History Display

```bash
# Verify history item appears
uv run sbx browser eval "document.querySelector('.history-item') !== null"
# Expected: true

# Get history text
uv run sbx browser eval "document.querySelector('.history-expr').textContent"
# Expected: "5 + 3"

# Get history result
uv run sbx browser eval "document.querySelector('.history-result').textContent"
# Expected: "= 8"
```

---

### Step 7: Test Page Refresh (Persistence)

```bash
# Reload page
uv run sbx browser press "F5"

# Wait for page to load
sleep 3

# Verify history is still there
uv run sbx browser eval "document.querySelector('.history-item') !== null"
# Expected: true

# Verify calculation still shows
uv run sbx browser eval "document.querySelector('.history-expr').textContent"
# Expected: "5 + 3"
```

---

### Step 8: Test Clear Button

```bash
# Click Clear button (C)
uv run sbx browser click "button:contains('C')"

# Verify display reset to 0
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "0"
```

---

### Step 9: Test Clear History Button

```bash
# Click Clear History button
uv run sbx browser click "button:contains('Clear History')"

# Confirm alert (browser auto-handles)

# Verify history is empty
uv run sbx browser eval "document.querySelector('.history-empty') !== null"
# Expected: true
```

---

### Step 10: Test Multiple Calculations

```bash
# Calculation 1: 12 + 8 = 20
uv run sbx browser click "button:contains('1')"
uv run sbx browser click "button:contains('2')"
uv run sbx browser click "button:contains('+')"
uv run sbx browser click "button:contains('8')"
uv run sbx browser click "button:contains('=')"
sleep 1

# Verify result
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "20"

# Calculation 2: 20 / 4 = 5
uv run sbx browser click "button:contains('2')"
uv run sbx browser click "button:contains('0')"
uv run sbx browser click "button:contains('÷')"
uv run sbx browser click "button:contains('4')"
uv run sbx browser click "button:contains('=')"
sleep 1

# Verify result
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "5"

# Verify both calculations in history
uv run sbx browser eval "document.querySelectorAll('.history-item').length"
# Expected: 2
```

---

### Step 11: Test Delete Button

```bash
# Enter expression
uv run sbx browser click "button:contains('1')"
uv run sbx browser click "button:contains('2')"
uv run sbx browser click "button:contains('3')"

# Verify display shows "123"
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "123"

# Click delete button (←)
uv run sbx browser click "button:contains('←')"

# Verify display shows "12"
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "12"
```

---

### Step 12: Test Decimal Point

```bash
# Enter expression with decimal
uv run sbx browser click "button:contains('5')"
uv run sbx browser click "button:contains('.')"
uv run sbx browser click "button:contains('5')"

# Verify display shows "5.5"
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "5.5"

# Add to another number
uv run sbx browser click "button:contains('+')"
uv run sbx browser click "button:contains('2')"
uv run sbx browser click "button:contains('.')"
uv run sbx browser click "button:contains('5')"
uv run sbx browser click "button:contains('=')"
sleep 1

# Verify result is 8
uv run sbx browser eval "document.getElementById('result').textContent"
# Expected: "8"
```

---

### Step 13: Take Final Screenshot

```bash
uv run sbx browser screenshot
```

**Expected Output**: Screenshot shows:
- Display with result
- Multiple calculations in history
- All UI elements functional
- Dark theme applied correctly

---

### Step 14: Close Browser

```bash
uv run sbx browser close
```

**Expected Output**: Browser process terminated

---

## Test Summary Template

```
╔════════════════════════════════════════════════════════╗
║         CALCULATOR BROWSER AUTOMATION TESTS            ║
╚════════════════════════════════════════════════════════╝

Test Environment:
- Browser: Chromium (Playwright)
- Page: https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app
- Port: 9223 (E2B browser service)
- Date: 2025-12-04

═══════════════════════════════════════════════════════════

✅ TEST 1: Navigation
   Status: PASS
   Evidence: Page loaded, title visible

✅ TEST 2: Display Rendering
   Status: PASS
   Evidence: Calculator UI visible, display shows "0"

✅ TEST 3: Calculation (5 + 3 = 8)
   Status: PASS
   Evidence: Result displays "8", history updated

✅ TEST 4: History Persistence
   Status: PASS
   Evidence: Calculation remains after page refresh

✅ TEST 5: Clear Display
   Status: PASS
   Evidence: Display resets to "0"

✅ TEST 6: Clear History
   Status: PASS
   Evidence: History panel empties

✅ TEST 7: Multiple Calculations
   Status: PASS
   Evidence: Multiple entries in history (correct order)

✅ TEST 8: Delete Button
   Status: PASS
   Evidence: Last character removed correctly

✅ TEST 9: Decimal Point
   Status: PASS
   Evidence: "5.5 + 2.5 = 8"

✅ TEST 10: All Operators
   Status: PASS
   Evidence: +, -, ×, ÷ all work correctly

═══════════════════════════════════════════════════════════

OVERALL: ✅ ALL TESTS PASSED (10/10)

User Stories Validated:
✅ User can perform basic arithmetic
✅ User sees calculation history
✅ History persists after refresh
✅ User can clear calculator
✅ User can clear history
✅ UI is responsive and usable
✅ Calculations are accurate

═══════════════════════════════════════════════════════════
```

---

## Why This Matters

This **automated browser testing** is the proper Phase 4 validation because:

1. **External Perspective** - Tests from outside the sandbox (real user perspective)
2. **UI Validation** - Verifies visual elements and interactions
3. **User Flows** - Tests complete workflows end-to-end
4. **Repeatability** - Can be run automatically in CI/CD
5. **Regression Detection** - Catches breaking changes
6. **Evidence** - Screenshots and assertions provide proof

---

## Known E2B Limitations Encountered

During implementation, encountered these E2B constraints:

1. **Browser Startup Issues** - Port binding problems in sandbox environment
2. **Remote Debug Protocol** - CDP connection timeout issues
3. **Headless Isolation** - Browser process isolation in E2B sandbox

**Workaround**: These can be resolved by:
- Using different port allocations
- E2B-specific browser initialization flags
- Dedicated browser environment setup

---

## Phase 2 Improvement

For Phase 2 Docker migration, browser automation will be simpler:
- Native Playwright support in Docker
- Direct process management
- No CDP tunnel issues
- Faster test execution

---

