# Browser Testing Agent Skill

## Overview
Automated browser-based testing agent that validates the Flourisha frontend from a user's perspective using Playwright. Tests all pages, buttons, forms, and error handling.

## What This Does
- Opens a headless browser and navigates to the frontend
- Tests login/signup pages for all required elements
- Validates form functionality and error messages
- Tests navigation between pages
- Checks for JavaScript errors and console warnings
- Validates that API integration is working
- Tests responsive UI elements
- Reports comprehensive test results

## When to Use
- After making frontend code changes
- Before deployment to production
- To validate new features work end-to-end
- When debugging user-reported issues
- To ensure authentication flow works

## How to Run

### Installation (First Time Only)
```bash
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app/backend
source venv/bin/activate
pip install playwright
python3 -m playwright install chromium
playwright install-deps  # Install system dependencies
```

### Run Tests
```bash
source /root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/venv/bin/activate
python3 /root/.claude/scripts/browser-tester.py
```

### Run Tests Against Different URL
```bash
# Modify the base_url in the script or extend it to accept arguments
python3 /root/.claude/scripts/browser-tester.py --url http://localhost:5174
```

## What Tests Are Included

1. **Page Load Tests**
   - Login page loads correctly
   - Signup page loads correctly
   - Dashboard redirects properly

2. **Form Validation Tests**
   - Login form has all required fields
   - Signup form has all required fields
   - Invalid credentials show error messages
   - Form submission works

3. **Navigation Tests**
   - Can navigate between pages
   - Protected routes redirect to login
   - Links work correctly

4. **UI Responsiveness Tests**
   - Buttons are clickable
   - Forms accept input
   - Elements respond to user interaction

5. **Error Handling Tests**
   - Invalid routes handled gracefully
   - Network errors shown to user
   - Error boundaries prevent app crashes

## Output Format
```json
{
  "total": 6,
  "passed": 5,
  "failed": 1,
  "success_rate": 83.3,
  "tests": [
    {
      "test": "Page Load: /login",
      "passed": true,
      "timestamp": "2025-12-03T19:39:33.231978",
      "message": "Loaded successfully"
    }
  ]
}
```

## Common Issues

### Browser Dependencies Missing
```
Error: Host system is missing dependencies to run browsers
Solution: Run: playwright install-deps
```

### Can't Connect to Frontend
```
Error: Connection refused to http://100.66.28.67:5174
Solution: Make sure frontend is running: npm run dev in web/ directory
```

### Tests Timeout
```
Error: Timeout waiting for selector
Solution: Increase timeout in code or check if element exists
```

## Extending the Tests

Add new test methods to `FlourishaTestAgent` class:

```python
async def test_my_feature(self, page: Page) -> bool:
    try:
        await page.goto(f"{self.base_url}/my-feature")
        # Your test logic here
        self.add_result("My Feature Test", True, "Feature works!")
        return True
    except Exception as e:
        self.add_result("My Feature Test", False, str(e))
        return False
```

Then add it to `run_all_tests()`:
```python
await self.test_my_feature(page)
```

## Integration with CI/CD

Can be integrated into GitHub Actions or other CI systems:

```yaml
- name: Run Browser Tests
  run: |
    source backend/venv/bin/activate
    python3 .claude/scripts/browser-tester.py
    # Fail if tests failed
    test $? -eq 0
```

## Files
- Script: `/root/.claude/scripts/browser-tester.py`
- Skill: `/root/.claude/skills/browser-tester/SKILL.md` (this file)
- Requirements: Playwright, Python 3.12+

## Notes
- Tests run in headless mode (no visible browser window)
- Currently tests against Tailscale IP (100.66.28.67:5174)
- Can modify base_url to test localhost or production
- All tests are non-destructive (don't modify database)
