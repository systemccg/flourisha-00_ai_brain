---
name: flourisha-sandbox
description: Execute Flourisha agent tasks in isolated E2B sandboxes with disler's proven prompt engineering patterns. USE WHEN building full-stack applications, running untrusted code, testing packages, or needing isolated execution environments. Integrates E2B templates, multi-step validation, and comprehensive specifications.
---

# Flourisha Sandbox Execution

Build full-stack applications, run isolated code, and validate complex workflows using disler's tested patterns and E2B sandboxes.

## Quick Start

### 1. Simple Code Execution in Sandbox

```bash
# Ensure E2B_API_KEY is set in ~/.claude/.env
# Then use agent-sandboxes skill for direct execution

\agent-sandboxes:exec-python "
import json
data = {'hello': 'flourisha'}
print(json.dumps(data, indent=2))
"
```

### 2. Build a Full-Stack Application

```
User: "Build a simple calculator app"

This skill will:
1. Create comprehensive specification following disler's template
2. Initialize E2B sandbox with fullstack-vue-fastapi-node22
3. Implement frontend (Vite + Vue 3), backend (FastAPI), database (SQLite)
4. Expose public URL and validate from outside
5. Run comprehensive browser UI tests
```

### 3. Test Code in Isolation

```
User: "Test this Python library in isolation"

This skill will:
1. Create sandbox with testing template
2. Upload your code
3. Run tests with isolated dependencies
4. Report results without affecting local system
```

## How It Works

### The Disler Pattern (4 Phases)

```
PHASE 1: PLAN
  ↓ Specification with 8+ detailed sections
  ↓ Success criteria defined and testable
  ↓ Output: path_to_plan

PHASE 2: BUILD
  ↓ Implement in E2B sandbox
  ↓ Run all validation commands from spec
  ↓ Output: Working application

PHASE 3: HOST
  ↓ Start frontend and backend
  ↓ Expose public URL
  ↓ Test from OUTSIDE sandbox
  ↓ Output: Public URL verified

PHASE 4: TEST
  ↓ Run comprehensive validation
  ↓ Browser UI testing (if applicable)
  ↓ Verify all success criteria
  ↓ Output: Pass/fail report
```

### Key Concepts

**E2B Sandboxes**: Isolated execution environments with:
- Pre-built templates (Vite + Vue 3 + FastAPI + SQLite)
- Automatic resource allocation (2-8 vCPU, 2-8GB RAM)
- 12-hour auto-termination (prevent runaway costs)
- Public URL exposure for testing
- Full filesystem access for agents

**Disler's Principles Applied**:
1. ✅ Detailed specifications prevent ambiguity
2. ✅ Sequential workflows with output capture
3. ✅ Multi-step validation catches failures early
4. ✅ Standardized stacks eliminate architecture decisions
5. ✅ Explicit instructions ensure reliability

**Output Capture**: Each phase produces artifacts that feed the next phase:
- PLAN → `path_to_plan` (specification file)
- BUILD → `sandbox_id` (captured from init)
- HOST → `public_url` (verified with curl)
- TEST → `validation_report` (against success criteria)

## Available Commands

### Direct E2B Access (Advanced)

Use the underlying `agent-sandboxes` skill for low-level sandbox operations:

```bash
# Initialize sandbox with template
\agent-sandboxes:init --template fullstack-vue-fastapi-node22

# Execute command in sandbox
\agent-sandboxes:exec [sandbox_id] "python script.py"

# Upload/download files
\agent-sandboxes:upload [sandbox_id] local.py remote/script.py
\agent-sandboxes:download [sandbox_id] remote/output.txt local.txt

# File operations
\agent-sandboxes:ls [sandbox_id] /path
\agent-sandboxes:read [sandbox_id] /path/file.txt

# Lifecycle
\agent-sandboxes:kill [sandbox_id]  # Terminate (rare)
\agent-sandboxes:get-host [sandbox_id]  # Get public URL
```

### Flourisha Workflows (Recommended)

These higher-level commands follow disler's patterns:

```bash
# Build full-stack app (all 4 phases automatically)
\flourisha-sandbox:build-app [user_prompt]

# Plan only (output specification file for manual review)
\flourisha-sandbox:plan [user_prompt]

# Build with custom specification
\flourisha-sandbox:build [path_to_plan]

# Test application after deployment
\flourisha-sandbox:test [sandbox_id] [public_url]
```

## Configuration

### Prerequisites

1. **E2B API Key** (already configured):
   ```bash
   # Verify in ~/.claude/.env
   grep E2B_API_KEY ~/.claude/.env
   ```

2. **Agent Prerequisites** (automatic):
   - CORE skill loaded (workflow notifications)
   - agent-sandboxes skill available
   - Task tool for multi-agent support

### Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `E2B_API_KEY` | E2B authentication | ✅ Yes | `e2b_4f...` |
| `PAI_DIR` | Flourisha brain location | ✅ Yes | `/root/flourisha/00_AI_Brain/` |
| `ENGINEER_NAME` | For personalized messages | Optional | `Greg` |

## Templates Available

| Template | Size | Cost | Best For |
|----------|------|------|----------|
| `fullstack-vue-fastapi-node22` | 2vCPU, 2GB RAM | $0.13/hr | Default (simple apps) |
| `fullstack-vue-fastapi-node22-lite` | 2vCPU, 4GB RAM | $0.15/hr | Browser testing |
| `fullstack-vue-fastapi-node22-standard` | 4vCPU, 4GB RAM | $0.27/hr | Parallel builds |
| `fullstack-vue-fastapi-node22-heavy` | 4vCPU, 8GB RAM | $0.33/hr | Heavy workloads |
| `fullstack-vue-fastapi-node22-max` | 8vCPU, 8GB RAM | $0.44/hr | Maximum speed |

## Example: Build Calculator App

### User Request
```
"Build a simple calculator web app with calculation history"
```

### Phase 1: Plan
Flourisha creates specification with:
- Value Proposition: "Basic calculator demonstrating full-stack integration"
- Core Features: Number buttons, operations (+,-,*,/), history, persistence
- Technical Requirements: SQLite schema, FastAPI endpoints, Vue 3 UI
- Implementation Details: Calculation logic, database operations
- Success Criteria: 12 testable checkboxes (number buttons work, history persists, etc.)

### Phase 2: Build
In E2B sandbox:
- ✅ Frontend: Vite + Vue 3 app with calculator UI
- ✅ Backend: FastAPI with POST /api/calculate, GET /api/history endpoints
- ✅ Database: SQLite with calculations table, auto-timestamp
- ✅ Validation: All success criteria commands run and pass

### Phase 3: Host
- ✅ Frontend starts on port 5173
- ✅ Backend starts on port 8000
- ✅ Public URL generated and tested with curl from outside
- ✅ CORS properly configured

### Phase 4: Test
- ✅ Browser UI: Click buttons, verify calculations
- ✅ API: Test all endpoints with curl
- ✅ Database: Verify persistence across page refresh
- ✅ All 12 success criteria verified

**Result**: Working calculator app at `https://[sandbox-id].e2b.host`

---

## Important Notes

### DO
- ✅ Use E2B for isolated, experimental work
- ✅ Let sandboxes auto-terminate (12-hour timeout)
- ✅ Test applications from OUTSIDE the sandbox
- ✅ Capture output between phases
- ✅ Document comprehensive specifications

### DON'T
- ❌ Store sensitive data in sandboxes (E2B is isolated but not encrypted)
- ❌ Leave sandboxes running unnecessarily (costs accumulate)
- ❌ Use placeholder values (capture actual outputs only)
- ❌ Skip testing phases (validation catches errors early)
- ❌ Manually kill sandboxes (let them auto-terminate)

## Phase 2: Docker Optimization (Coming Soon)

After Phase 1 validation, migration to Docker will:
- Use existing Contabo infrastructure (free)
- Replace E2B for cost savings
- Maintain same workflow patterns
- No changes to specification/validation approach

See: `/root/flourisha/00_AI_Brain/documentation/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md` for strategy details.

---

## Quick Reference

**Need to...** | **Command** | **Output**
---|---|---
Build an app | `\flourisha-sandbox:build-app "description"` | Public URL + test report
Plan only | `\flourisha-sandbox:plan "description"` | Specification file
Execute Python | `\agent-sandboxes:exec [id] "python script.py"` | Command output
Upload file | `\agent-sandboxes:upload [id] local remote` | File transferred
Check sandbox | `\agent-sandboxes:get-host [id]` | Public URL
Terminate | `\agent-sandboxes:kill [id]` | Sandbox stopped

---

## Support & References

- **Disler's Principles**: `/root/flourisha/00_AI_Brain/documentation/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md`
- **E2B Documentation**: https://e2b.dev/docs
- **Calculator Example**: `/tmp/agent-sandbox-skill/prompts/full_stack/sonnet/very_easy_calculator.md`
- **Workflow Pattern**: `/tmp/agent-sandbox-skill/.claude/skills/agent-sandboxes/prompts/plan-build-host-test.md`

