# Flourisha Frontend Dashboard - Coding Agent

## YOUR ROLE

You are a coding agent continuing development of the Flourisha Frontend Dashboard. The project has been initialized - your job is to implement features from ClickUp tasks.

## CRITICAL: Tiered Document Loading

**Minimize context usage with tiered loading:**

### Tier 1: Always Load First
```
/root/flourisha/00_AI_Brain/frontend/.clickup_project.json
```
Contains ClickUp list ID and META task ID.

### Tier 2: Load for Implementation Context
| Document | When to Load |
|----------|--------------|
| `flourisha_frontend_spec.md` | Architecture questions |
| `FRONTEND_FEATURE_REGISTRY.md` | Detailed UI requirements for specific feature |
| `api_backend_summary.md` | API endpoint details |

**DO NOT load all documents. Load only what you need for current task.**

---

## ClickUp API (Use clickup_api.py - NO MCP)

### Python API Client

Located at: `/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference/clickup_api.py`

```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()

# Get tasks
tasks = client.get_list_tasks(list_id="LIST_ID", statuses=["to do"])

# Update task status
client.update_task(task_id="xxx", status="in progress")

# Add comment
client.add_comment(task_id="xxx", comment_text="Implementation notes...")
```

---

## Session Start Checklist

### 0. Verify Git Remote (CRITICAL)
```bash
git -C /root/flourisha/00_AI_Brain/frontend remote -v
```
**If no remote configured, STOP and alert user.**

### 1. Read Project State
```
/root/flourisha/00_AI_Brain/frontend/.clickup_project.json
```

### 2. Check for User Feedback
```python
comments = client.get_comments("META_TASK_ID")
for c in comments[-3:]:
    print(c.get('comment_text', '')[:500])
```

### 3. Start Dev Server
```bash
cd /root/flourisha/00_AI_Brain/frontend && bun run dev &
```

### 4. Verify Previous Work
Open http://localhost:3000 in browser (use Puppeteer MCP if available)

---

## Work Process

### 1. Select Task from ClickUp
```python
tasks = client.get_list_tasks("LIST_ID", statuses=["to do"])
for t in sorted(tasks, key=lambda x: x.get('priority', {}).get('priority', 3))[:5]:
    print(f"{t['id']}: {t['name']}")
```

### 2. Claim Task
```python
client.update_task(task_id="TASK_ID", status="in progress")
```

### 3. Load Task Context
- Read spec file for feature requirements
- Check FRONTEND_FEATURE_REGISTRY.md section if UI details unclear
- Read API endpoint documentation if needed

### 4. Implement
Following Next.js 14+ App Router patterns:
- Pages in `app/` directory
- Components in `components/`
- API client in `lib/`
- Hooks in `hooks/`

### 5. Test (CRITICAL - Use All Testing Tools)

**A. Static Analysis (Quick)**
```bash
bun run type-check && bun run lint
```

**B. E2E Tests with Playwright (Required for UI changes)**
```bash
# Run smoke tests after any change
bun run test:e2e:smoke

# Run full E2E suite for feature completion
bun run test:e2e

# Run with visible browser for debugging
bun run test:e2e:headed
```

**C. Visual Verification**
- Open http://100.66.28.67:3002 in browser
- Test all affected user flows manually
- Screenshot any issues for ClickUp comments

**D. API Integration Testing**
```bash
# Verify API connectivity
curl -s http://100.66.28.67:8001/api/health | jq

# Test specific endpoints used by your feature
curl -s http://100.66.28.67:8001/api/[endpoint] | jq
```

### 5.1 Adding E2E Tests for New Features

When implementing a new feature, ADD corresponding E2E tests in `/e2e/`:

```typescript
// e2e/[feature].spec.ts
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('user can perform action', async ({ page }) => {
    await page.goto('/dashboard/feature');
    await expect(page.locator('[data-testid="feature-element"]')).toBeVisible();
    // Test user interactions
  });
});
```

**Test file naming:** `e2e/[feature].spec.ts` (e.g., `okrs.spec.ts`, `energy.spec.ts`)

### 6. Complete
```python
client.add_comment(task_id="TASK_ID", comment_text="Implemented: [description]")
client.update_task(task_id="TASK_ID", status="complete")
```
```bash
git add . && git commit -m "feat: [description]" && git push
```

---

## Code Standards

### Component Template

```tsx
'use client';

import { Box, Heading } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

interface Props {
  // Props
}

export function ComponentName({ }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['key'],
    queryFn: () => api.get('/endpoint').then(res => res.data),
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorDisplay error={error} />;

  return (
    <Box>
      <Heading>Title</Heading>
      {/* Content */}
    </Box>
  );
}
```

### API Hook Template

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, APIResponse } from '@/lib/api';

export function useFeature() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['feature'],
    queryFn: async () => {
      const { data } = await api.get<APIResponse<FeatureData>>('/feature');
      return data.data;
    },
  });

  const mutation = useMutation({
    mutationFn: (payload: CreatePayload) =>
      api.post<APIResponse<FeatureData>>('/feature', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature'] });
    },
  });

  return { ...query, create: mutation };
}
```

### Page Template (App Router)

```tsx
// app/dashboard/feature/page.tsx
import { Metadata } from 'next';
import { FeatureComponent } from '@/components/feature';

export const metadata: Metadata = {
  title: 'Feature | Flourisha',
};

export default function FeaturePage() {
  return <FeatureComponent />;
}
```

---

## File Ownership

| Directory | Action |
|-----------|--------|
| `frontend/app/` | CREATE/MODIFY - pages |
| `frontend/components/` | CREATE/MODIFY - UI components |
| `frontend/lib/` | CREATE/MODIFY - utilities |
| `frontend/hooks/` | CREATE/MODIFY - custom hooks |
| `documentation/` | READ ONLY |
| `agents/` | READ ONLY |

---

## API Endpoints Reference

### Authentication
```
POST /api/auth/login     - { email, token }
GET  /api/auth/me        - Current user
POST /api/auth/logout    - End session
```

### Search
```
POST /api/search         - { query, filters, limit }
```

### Knowledge
```
GET  /api/graph/query    - { cypher }
GET  /api/para/browse    - { path }
```

### OKRs
```
GET  /api/okrs           - ?quarter=Q1_2026
POST /api/okrs/measure   - { kr_id, value, notes }
```

### Energy
```
POST /api/energy         - { level, focus_quality, task }
GET  /api/energy/history - ?days=7
```

### Skills
```
GET  /api/skills         - List all skills
POST /api/skills/:id/execute - Execute skill
```

### Health
```
GET  /api/health/dashboard - Service statuses
```

---

## Sub-Agent Delegation (Parallel Work)

**Use Task tool to delegate work to specialized sub-agents:**

### When to Delegate

| Task Type | Agent Type | Use Case |
|-----------|------------|----------|
| Code exploration | `Explore` | Find patterns, understand codebase |
| Testing verification | `engineer` | Run tests, verify implementations |
| Research | `researcher` | Look up API docs, library usage |
| Code review | `engineer` | Review your own code before commit |

### Parallel Testing Pattern

After implementing a feature, launch parallel agents:

```
# In your response, use multiple Task tool calls:

Task 1 (engineer): "Run bun run type-check and bun run lint in /root/flourisha/00_AI_Brain/frontend and report any errors"

Task 2 (engineer): "Run bun run test:e2e:smoke in /root/flourisha/00_AI_Brain/frontend and report test results"

Task 3 (Explore): "Verify the new [component] follows patterns in existing components at /root/flourisha/00_AI_Brain/frontend/src/components"
```

### Model Selection for Agents

| Task Complexity | Model | Why |
|-----------------|-------|-----|
| Simple verification | `haiku` | Fast, sufficient for checking |
| Standard implementation | `sonnet` | Good balance |
| Complex architecture | `opus` | Maximum reasoning |

---

## Sandbox Usage (Docker)

For isolated testing or risky operations, use docker-sandbox:

```bash
# Run commands in isolated container
docker run --rm -v /root/flourisha/00_AI_Brain/frontend:/app -w /app node:20 bun run build

# Test installation from scratch
docker run --rm -v /root/flourisha/00_AI_Brain/frontend:/app -w /app node:20 bash -c "bun install && bun run type-check"
```

**When to use sandbox:**
- Testing fresh installs (no cached node_modules)
- Running potentially breaking builds
- Verifying CI/CD would pass

---

## Session End Protocol

Before context fills:

1. **Commit and PUSH** all code changes
2. **Update** completed tasks in ClickUp
3. **Comment** on META task:
```python
client.add_comment(
    task_id="META_TASK_ID",
    comment_text="""SESSION N COMPLETE

ACCOMPLISHED:
* Task descriptions

FILES MODIFIED:
* frontend/app/feature/page.tsx
* frontend/components/feature.tsx

RECOMMENDED NEXT:
* Task ID - reason"""
)
```

---

## Quick Reference

| Item | Value |
|------|-------|
| Timezone | Pacific (PST/PDT) |
| Package Manager | bun (NOT npm) |
| Framework | Next.js 14+ App Router |
| UI Library | Chakra UI |
| State | TanStack React Query |
| API Base | http://100.66.28.67:8001/api |

---

## Critical Rules

1. **One task at a time** - complete before starting next
2. **ClickUp is truth** - don't update markdown status
3. **Use bun** - never npm/yarn/pnpm
4. **App Router** - not pages directory
5. **Type everything** - strict TypeScript
6. **Test with Playwright** - run `bun run test:e2e:smoke` after UI changes
7. **Visual verification** - check http://100.66.28.67:3002
8. **Push immediately** - don't lose work
9. **Add E2E tests** - every new feature needs a test file
10. **Use sub-agents** - parallelize testing with Task tool
