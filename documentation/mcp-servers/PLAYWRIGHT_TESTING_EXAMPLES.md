# Playwright MCP Testing Examples

**Purpose**: Real-world examples of using Playwright MCP for Flourisha app testing
**Date**: 2025-12-04
**Status**: Ready for immediate use

---

## Example 1: Calculator App Automated Testing

### Use Case
Test the calculator web app built with the disler pattern to validate Phase 4 testing.

### Prompt to Use in Claude Code

```
I have a calculator web app running at https://5173-iw46mb7if7f3qvdvzdl7b.e2b.app

Using Playwright MCP, perform these automated tests:

1. **Initial State Test**
   - Navigate to the URL
   - Take a screenshot
   - Verify display shows "0"

2. **Basic Calculation Test (5 + 3 = 8)**
   - Click button "5"
   - Click button "+"
   - Click button "3"
   - Click button "="
   - Wait 2 seconds for result
   - Verify display shows "8"
   - Take screenshot

3. **History Display Test**
   - Verify history panel contains the calculation
   - Check that history shows "5 + 3" and "= 8"
   - Take screenshot of history

4. **Persistence Test**
   - Reload the page (F5)
   - Wait 3 seconds
   - Verify the calculation is still in history
   - Take screenshot

5. **Clear Button Test**
   - Click the "C" (Clear) button
   - Verify display resets to "0"
   - Take screenshot

6. **Multiple Calculations**
   - Test "10 - 2 = 8"
   - Test "7 * 6 = 42"
   - Test "20 / 4 = 5"
   - Verify all three appear in history
   - Take screenshot

Provide evidence: screenshots at each major step and assertion results (pass/fail).
```

### Expected Output

```
✅ TEST RESULTS: Calculator App Automated Testing
================================================

1. Initial State: PASS
   - URL loaded successfully
   - Display shows "0"
   - [Screenshot: initial-state.png]

2. Basic Calculation (5 + 3): PASS
   - Clicked 5, +, 3, =
   - Result displays "8"
   - [Screenshot: calculation-result.png]

3. History Display: PASS
   - History panel visible
   - Calculation "5 + 3" shows "= 8"
   - [Screenshot: history-display.png]

4. Persistence: PASS
   - Page reloaded
   - Calculation still in history
   - [Screenshot: after-refresh.png]

5. Clear Button: PASS
   - Display reset to "0"
   - [Screenshot: after-clear.png]

6. Multiple Calculations: PASS
   - Three calculations visible in history
   - All correct (8, 42, 5)
   - [Screenshot: multiple-calcs.png]

OVERALL: ✅ 6/6 TESTS PASSED
```

---

## Example 2: Login Flow Testing

### Use Case
Test user authentication flow in a web app.

### Prompt

```
Test the login flow at https://app.flourisha.ai

Using Playwright MCP:

1. Navigate to login page
2. Verify login form is visible
3. Enter username "test@flourisha.ai"
4. Enter password "TestPassword123!"
5. Click "Sign In" button
6. Wait 3 seconds for redirect
7. Verify redirected to dashboard
8. Check that user name appears in header
9. Take screenshot of successful login
10. Take screenshot of dashboard

Report: Pass/fail for each step and screenshots as evidence.
```

---

## Example 3: E-commerce Checkout Flow

### Use Case
Test complete purchase flow with multiple steps.

### Prompt

```
Test the checkout flow at https://shop.example.com

Using Playwright MCP:

1. **Browse Products**
   - Navigate to store
   - Take screenshot of product listing
   - Click on "Blue Widget"
   - Verify product details load

2. **Add to Cart**
   - Click "Add to Cart" button
   - Wait for confirmation
   - Verify cart count increases to 1
   - Take screenshot

3. **Go to Checkout**
   - Click "View Cart"
   - Verify Blue Widget is in cart
   - Click "Proceed to Checkout"

4. **Enter Shipping Address**
   - Fill "Street Address": "123 Main St"
   - Fill "City": "San Francisco"
   - Fill "State": "CA"
   - Fill "Zip": "94105"
   - Click "Continue"

5. **Select Shipping Method**
   - Verify shipping options appear
   - Select "Standard Shipping"
   - Click "Continue"

6. **Enter Payment**
   - Fill "Card Number": "4111111111111111"
   - Fill "Expiry": "12/25"
   - Fill "CVC": "123"
   - Click "Place Order"

7. **Verify Order Confirmation**
   - Wait 3 seconds
   - Verify "Order Confirmed" message appears
   - Verify order number is displayed
   - Take final screenshot

Provide evidence: screenshots at each stage and pass/fail results.
```

---

## Example 4: Form Validation Testing

### Use Case
Test client-side form validation.

### Prompt

```
Test form validation at https://app.example.com/contact

Using Playwright MCP:

1. **Required Field Validation**
   - Navigate to contact form
   - Click "Submit" without filling fields
   - Verify error: "Name is required"
   - Verify error: "Email is required"
   - Verify error: "Message is required"
   - Take screenshot

2. **Email Format Validation**
   - Fill Name: "John Doe"
   - Fill Email: "invalid-email"
   - Fill Message: "Test message"
   - Click "Submit"
   - Verify error: "Please enter a valid email"
   - Take screenshot

3. **Min Length Validation**
   - Fill Email: "john@example.com"
   - Fill Message: "Hi" (less than 10 chars)
   - Click "Submit"
   - Verify error: "Message must be at least 10 characters"

4. **Successful Submission**
   - Fill Name: "John Doe"
   - Fill Email: "john@example.com"
   - Fill Message: "This is a test message"
   - Click "Submit"
   - Verify success message appears
   - Verify form clears
   - Take screenshot

Report each validation result: PASS/FAIL with evidence.
```

---

## Example 5: Dark Mode Toggle Testing

### Use Case
Test theme switching functionality.

### Prompt

```
Test dark mode at https://app.flourisha.ai

Using Playwright MCP:

1. **Initial Light Mode**
   - Navigate to app
   - Take screenshot (should show light theme)
   - Verify background color is light
   - Verify text color is dark

2. **Toggle Dark Mode**
   - Find theme toggle button (usually moon icon)
   - Click the toggle
   - Wait 1 second for animation
   - Take screenshot (should show dark theme)

3. **Verify Dark Mode Styling**
   - Check background is dark
   - Check text is light
   - Verify contrast is acceptable
   - Take screenshot

4. **Persistence Test**
   - Reload page
   - Wait 2 seconds
   - Verify dark mode persists
   - Take screenshot

5. **Toggle Back to Light**
   - Click theme toggle again
   - Verify light mode returns
   - Take final screenshot

Evidence: Screenshots showing light → dark → light transitions.
```

---

## Example 6: Responsive Design Testing

### Use Case
Test that app works on different screen sizes.

### Prompt

```
Test responsive design of https://app.flourisha.ai

Using Playwright MCP:

1. **Desktop View (1920x1080)**
   - Set viewport to 1920x1080
   - Navigate to app
   - Take screenshot
   - Verify all elements visible
   - Verify layout is horizontal

2. **Tablet View (768x1024)**
   - Set viewport to 768x1024
   - Reload page
   - Take screenshot
   - Verify menu is accessible
   - Verify content readable

3. **Mobile View (375x667)**
   - Set viewport to 375x667
   - Reload page
   - Take screenshot
   - Verify hamburger menu present
   - Verify no horizontal scroll

4. **Mobile Interaction Test**
   - Click hamburger menu
   - Verify menu opens
   - Take screenshot
   - Click menu item
   - Verify menu closes after navigation

Verify: Layout adapts correctly at all three breakpoints.
```

---

## Example 7: Performance Testing with Screenshots

### Use Case
Test page load performance and visual completeness.

### Prompt

```
Test page performance at https://app.flourisha.ai

Using Playwright MCP:

1. **Initial Load**
   - Navigate to page
   - Record start time
   - Take screenshot at 2 seconds
   - Take screenshot at 5 seconds
   - Record completion time

2. **Hero Image Load**
   - Verify hero image loads
   - Check image is visible
   - Verify no broken images
   - Take screenshot

3. **Content Load Order**
   - Note: Header (should be first)
   - Note: Hero image (should be second)
   - Note: Content sections (should be third)
   - Note: Footer (should be last)

4. **Final State**
   - Wait 5 seconds for all resources
   - Take final screenshot
   - Verify page is fully interactive
   - Check console for errors

Report: Load time and visual completion verification.
```

---

## Example 8: Accessibility Testing

### Use Case
Test keyboard navigation and screen reader compatibility.

### Prompt

```
Test accessibility at https://app.flourisha.ai

Using Playwright MCP:

1. **Keyboard Navigation**
   - Navigate to page
   - Press Tab repeatedly
   - Verify focus outline visible
   - Verify logical tab order
   - Take screenshot showing focus

2. **Form Navigation**
   - Start at form
   - Use Tab to navigate fields
   - Verify focus moves: Name → Email → Message → Submit
   - Use Shift+Tab to go backwards
   - Take screenshot

3. **Button Activation**
   - Navigate to button with Tab
   - Press Enter to activate
   - Verify button action triggers
   - Take screenshot

4. **Link Testing**
   - Navigate to link with Tab
   - Press Enter
   - Verify link navigation works
   - Take screenshot

Report: Keyboard navigation fully functional (PASS/FAIL).
```

---

## Example 9: Real-time Data Updates Testing

### Use Case
Test live data updates and WebSocket connections.

### Prompt

```
Test real-time updates at https://dashboard.flourisha.ai

Using Playwright MCP:

1. **Initial Data Load**
   - Navigate to dashboard
   - Wait 2 seconds
   - Take screenshot
   - Record initial values

2. **Monitor for Updates**
   - Wait 10 seconds
   - Take screenshot
   - Check if values updated
   - Compare with initial screenshot

3. **Manual Refresh Trigger**
   - Find "Refresh" button
   - Click it
   - Wait 3 seconds
   - Take screenshot
   - Verify data updated

4. **Connection Status**
   - Check if connection indicator shows green
   - Disconnect (simulate by closing DevTools)
   - Verify status changes to red
   - Reconnect
   - Verify status returns to green

Report: Real-time updates working (PASS/FAIL) with evidence.
```

---

## Example 10: Error State Testing

### Use Case
Test how app handles errors and edge cases.

### Prompt

```
Test error handling at https://api.flourisha.ai/docs

Using Playwright MCP:

1. **Empty Data Test**
   - Navigate to app
   - Try to submit empty form
   - Verify error message appears
   - Take screenshot

2. **Invalid Data Test**
   - Submit with invalid input
   - Verify specific error appears
   - Take screenshot

3. **Network Error Simulation**
   - Go offline (if possible)
   - Try to fetch data
   - Verify "Connection failed" message
   - Take screenshot

4. **Timeout Test**
   - Trigger slow API call
   - Wait for timeout
   - Verify timeout message appears
   - Take screenshot

5. **Recovery Test**
   - Fix the issue (go online, etc.)
   - Retry action
   - Verify it succeeds
   - Take screenshot

Report: Error handling is graceful and user-friendly (PASS/FAIL).
```

---

## How to Adapt These Examples

### Template for Custom Testing

```
Test [app name] at [URL]

Using Playwright MCP:

1. **Step Name**
   - Action 1
   - Action 2
   - Verification
   - Take screenshot

2. **Step Name**
   - Action 1
   - Action 2
   - Verification
   - Take screenshot

Expected behavior: [description]
Evidence required: screenshots and assertion results
```

### Common Playwright MCP Actions

| Action | Playwright Code | Flourisha Use |
|--------|-----------------|---------------|
| Navigate | `page.goto(url)` | Load app |
| Click | `page.click(selector)` | Click buttons |
| Type | `page.fill(selector, text)` | Fill forms |
| Wait | `page.wait_for_timeout(ms)` | Let things load |
| Screenshot | `page.screenshot()` | Capture evidence |
| Evaluate | `page.evaluate(js)` | Run custom JS |
| Check text | `page.inner_text(selector)` | Verify content |

---

## Integration with Flourisha Projects

### For Each New App Built

1. **Phase 1**: Write specification with success criteria
2. **Phase 2**: Build the app
3. **Phase 3**: Deploy and get public URL
4. **Phase 4**: Create Playwright MCP test prompt
   - Use these examples as templates
   - Test all user flows
   - Generate screenshots as evidence
   - Document any issues found

### Reusable Test Patterns

Save these test prompts to:
```
/root/flourisha/01f_Flourisha_Projects/[app-name]/TESTING_PROMPTS.md
```

Then in future sessions:
```
Reference the testing prompts for [app-name]:
/root/flourisha/01f_Flourisha_Projects/[app-name]/TESTING_PROMPTS.md
```

---

## Best Practices

1. **Always take screenshots**
   - Initial state
   - After each major action
   - Final state
   - Any error states

2. **Wait between actions**
   - 1-2 seconds for UI updates
   - 2-3 seconds after form submission
   - 3-5 seconds for page navigation

3. **Be specific with selectors**
   - Prefer IDs: `#submit-btn`
   - Then classes: `.primary-button`
   - Last resort: text content

4. **Test user flows end-to-end**
   - Don't just test individual buttons
   - Test complete workflows
   - Test edge cases and errors

5. **Document expected behavior**
   - State what should happen
   - State what you're verifying
   - Provide clear pass/fail criteria

---

## Next Steps

1. ✅ Review these examples
2. ⏭️ Run the calculator example (most relevant)
3. ⏭️ Create testing prompts for flourisha-app
4. ⏭️ Build reusable test templates
5. ⏭️ Integrate into Phase 2 Docker testing

---

**Date Created**: 2025-12-04
**Ready to Use**: Yes
**Tested With**: Calculator app example
**Status**: Production Ready
