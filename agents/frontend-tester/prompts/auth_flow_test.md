# Authentication Flow Test Prompt

Test the complete authentication flow for the Flourisha frontend.

## Test Cases

### 1. Login Page Load
- Navigate to `http://100.66.28.67:3000/login`
- Verify page loads without errors
- Check for Firebase auth elements (email input, password input, Google OAuth button)

### 2. Invalid Credentials
- Enter invalid email/password
- Submit form
- Verify error message displays

### 3. Protected Route Redirect
- Navigate to `http://100.66.28.67:3000/dashboard` without authentication
- Verify redirect to `/login`

### 4. Get Started Button
- Navigate to homepage `http://100.66.28.67:3000`
- Click "Get Started" button
- Verify navigation to `/login`

## Commands

```bash
# Run specific auth tests
cd /root/flourisha/00_AI_Brain/frontend
npx playwright test e2e/get-started.spec.ts --project=chromium

# Interactive testing with MCP
# Use mcp__playwright__browser_navigate to go to /login
# Use mcp__playwright__browser_screenshot to capture state
```

## Success Criteria

- Login page renders all required elements
- Error states display correctly
- Navigation flows work as expected
- No console errors during auth flow
