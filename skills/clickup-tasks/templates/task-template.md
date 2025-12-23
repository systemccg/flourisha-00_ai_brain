# Task Template for Coding Projects

Use this template when creating ClickUp tasks for autonomous coding projects.

> **IMPORTANT:** Use the `markdown_description` field (not `description`) to ensure proper formatting in ClickUp UI.

---

## Task Name Format

`[Category] - [Brief Feature Name]`

Examples:
- `Auth - User login flow`
- `UI - Dashboard layout`
- `API - User endpoints`
- `Style - Dark mode toggle`

---

## Task Description Template

```markdown
## Feature Description
[1-2 sentences describing what this feature does and why it matters]

## Category
[functional | style | infrastructure]

## Test Steps
1. Navigate to [page/URL]
2. [Specific action to perform]
3. [Another action]
4. Verify [expected result]
5. [Additional verification steps]

## Acceptance Criteria
- [ ] [Specific measurable criterion 1]
- [ ] [Specific measurable criterion 2]
- [ ] [Specific measurable criterion 3]

## Technical Notes
[Optional: Implementation hints, dependencies, or constraints]
```

---

## Priority Guidelines

| Priority | Use For | Examples |
|----------|---------|----------|
| 1 (Urgent) | Foundational, blocking | Database setup, core API, basic layout |
| 2 (High) | Primary user features | Authentication, main functionality |
| 3 (Normal) | Secondary features | Settings, preferences, enhancements |
| 4 (Low) | Polish, nice-to-have | Animations, edge cases, minor UI tweaks |

---

## Example Task

**Name:** `Auth - User login flow`

**Priority:** 2 (High)

**API Payload:**
```json
{
  "name": "Auth - User login flow",
  "markdown_description": "## Feature Description\n\nImplement user authentication with email/password login. Users should be able to log in and access protected routes.\n\n## Category\n\n`functional`\n\n## Test Steps\n\n1. Navigate to `/login`\n2. Enter valid email and password\n3. Click \"Sign In\" button\n4. Verify redirect to dashboard\n5. Verify user info displayed in header\n6. Test invalid credentials show error message\n\n## Acceptance Criteria\n\n- [ ] Login form validates email format\n- [ ] Password field is masked\n- [ ] Success redirects to `/dashboard`\n- [ ] Error messages display for invalid credentials\n- [ ] Session persists on page refresh\n\n## Technical Notes\n\n- Use JWT tokens stored in httpOnly cookies\n- Implement rate limiting on login endpoint",
  "priority": 2,
  "status": "--"
}
```

**Rendered in ClickUp:**
```markdown
## Feature Description

Implement user authentication with email/password login. Users should be able to log in and access protected routes.

## Category

`functional`

## Test Steps

1. Navigate to `/login`
2. Enter valid email and password
3. Click "Sign In" button
4. Verify redirect to dashboard
5. Verify user info displayed in header
6. Test invalid credentials show error message

## Acceptance Criteria

- [ ] Login form validates email format
- [ ] Password field is masked
- [ ] Success redirects to `/dashboard`
- [ ] Error messages display for invalid credentials
- [ ] Session persists on page refresh

## Technical Notes

- Use JWT tokens stored in httpOnly cookies
- Implement rate limiting on login endpoint
```
