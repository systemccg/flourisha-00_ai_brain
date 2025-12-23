# Disler's Prompt Engineering Principles for Flourisha

**Source**: Analysis of disler (indydevdan) agent-sandbox-skill repository
**Analyzed**: 2025-12-04
**Context**: Foundation for Phase 1 agent-sandbox integration

---

## Executive Summary

Disler has developed a highly structured, reusable system for prompt engineering that enables AI agents to reliably execute complex, multi-step tasks. His approach emphasizes:

1. **Hierarchical Task Decomposition** - Breaking complex tasks into sequential, validated steps
2. **Explicit Output Capture** - Forcing agents to identify and preserve critical information between steps
3. **Success Criteria & Validation** - Testing at each layer to prevent cascade failures
4. **Standardized Stack Selection** - Pre-validated technology choices eliminate architecture decisions
5. **Template-Driven Development** - Using pre-built E2B templates with known configurations
6. **Workflow Orchestration** - Sequential pipelines (plan → build → host → test) with handoff validation

---

## Core Principles

### 1. The Specification Template (Detailed Scoping)

**Pattern**: Comprehensive scope definition with 8+ sections before implementation

**Structure**:
```
- Value Proposition (1-2 sentences of what it solves)
- Core Features (3-5 major capabilities)
- Technical Requirements (Schema, API, Frontend specifics)
- Implementation Details (Pseudocode/logic breakdown)
- Success Criteria (Testable requirements as checkboxes)
- Testing (Manual test flows + validation commands)
- Why This Works (Benefits summary)
- UI Design (Visual/UX specifications)
```

**Example** (from `very_easy_calculator.md`):
- 1 paragraph value prop
- 3 subsections of features (Display, Actions, Persistence)
- 3 backend API endpoints fully specified
- Database schema documented
- 12 success criteria checkboxes
- Manual test flow with exact steps
- curl validation commands included

**Key Insight**: The specification IS the implementation contract. It removes interpretation ambiguity and makes testing trivial (just verify checkboxes).

---

### 2. Sequential Workflow Orchestration (Plan → Build → Host → Test)

**Pattern**: Four discrete, sequential phases with output handoff

**Phase Structure**:
```
1. PLAN
   Output: Detailed specification file
   Artifact: path_to_plan (captured for next step)

2. BUILD
   Input: path_to_plan
   Output: Fully implemented application
   Artifact: confirmation of successful validation commands

3. HOST
   Input: sandbox_id
   Output: Public URL accessible from outside
   Artifact: [public_url] verified with curl

4. TEST
   Input: public_url, path_to_plan, sandbox_id
   Output: Comprehensive validation report
   Artifact: Pass/fail on all success criteria
```

**Critical**: Each step validates outputs before passing to next step. Failures block progression and provide debugging info.

---

### 3. Explicit Output Capture (Between-Step Communication)

**Pattern**: Force agents to identify and document critical information

**Implementation**:
- Each step produces specific artifacts
- Artifacts are NAMED and CAPTURED in working memory (not env vars, not files)
- Subsequent steps reference captured outputs
- No placeholder values - only actual execution results

**Example** (from plan-build-host-test.md):
```
Step 1: Init sandbox
  → Capture: sandbox_id (format: sbx_abc123def456)
  → Store in working memory

Step 2: Create plan
  → Use captured sandbox_id from Step 1
  → Capture: path_to_plan (actual file path)
  → Store in working memory

Step 3: Build
  → Use captured path_to_plan from Step 2
  → Use captured sandbox_id from Step 1
  → Build in that specific sandbox
  → Capture build completion status

Step 4: Host
  → Use captured sandbox_id
  → Port determined automatically
  → Capture: public_url from `sbx sandbox get-host`
  → Validate with curl from OUTSIDE sandbox
```

**Key Insight**: This prevents downstream steps from using stale/wrong data and makes debugging trivial (you can see exactly what was passed).

---

### 4. Standardized Stack Strategy (Eliminate Architecture Decisions)

**Pattern**: Pre-validated, pre-built technology combinations in E2B templates

**The Standard Stack**:
```
Frontend:   Vite 5.4.11 + Vue 3 + TypeScript + Pinia
Backend:    FastAPI + uvicorn + Python (managed by uv)
Database:   SQLite (auto-setup in schema)
Tools:      Node.js 22, uv (astral Python package manager)
```

**Template Tiers** (resource-cost tradeoff):
- `fullstack-vue-fastapi-node22` - 2vCPU, 2GB RAM ($0.13/hr) - Default
- `fullstack-vue-fastapi-node22-lite` - 2vCPU, 4GB RAM ($0.15/hr) - Browser tests
- `fullstack-vue-fastapi-node22-standard` - 4vCPU, 4GB RAM ($0.27/hr) - Parallel builds
- `fullstack-vue-fastapi-node22-heavy` - 4vCPU, 8GB RAM ($0.33/hr) - Multi-browser
- `fullstack-vue-fastapi-node22-max` - 8vCPU, 8GB RAM ($0.44/hr) - Fastest

**Why This Works**:
- Pre-built templates mean zero setup overhead
- All components tested together (no version conflicts)
- Resource allocation matches common workload patterns
- Cost predictable (per-hour billing, auto-terminate after 12 hours)

**Key Insight**: By eliminating architecture decisions, the focus shifts entirely to implementation quality.

---

### 5. E2B Integration Patterns (Safe Execution Environments)

**Pattern**: E2B sandboxes as the execution substrate

**Key Commands**:
```bash
# Initialize with template (captures sandbox_id)
sbx init --template fullstack-vue-fastapi-node22 --timeout 43200 --name [WORKFLOW_ID]

# File operations
sbx files ls /path
sbx files upload local.txt remote.txt
sbx files read /path/to/file

# Execute commands
sbx exec --sandbox-id [sandbox_id] "python script.py"
sbx exec --sandbox-id [sandbox_id] --shell "for f in *.py; do echo $f; done"

# Sandbox lifecycle
sbx sandbox get-host [sandbox_id]  # Get public URL
sbx sandbox extend-lifetime [sandbox_id] [hours]  # Keep it running
sbx sandbox kill [sandbox_id]  # Terminate (manual, rare)
```

**Isolation Benefits**:
- No pollution of local system
- Automatic cleanup after timeout (12 hours default)
- Full filesystem access for agent
- Network access with public URL exposure
- Cost control (metered by hour, terminate when done)

---

### 6. Multi-Step Validation (Prevent Cascade Failures)

**Pattern**: Test at every phase, not just the end

**Validation Layers**:
```
PLAN phase:
  ✓ Specification is detailed and unambiguous
  ✓ All success criteria are testable

BUILD phase:
  ✓ Frontend builds without errors
  ✓ Backend starts successfully
  ✓ Database schema created
  ✓ All validation commands from spec pass
  ✓ (Optional) npm test, pytest, etc.

HOST phase:
  ✓ Frontend accessible at public URL
  ✓ Backend accessible at public URL
  ✓ CORS properly configured
  ✓ Public URL works from OUTSIDE sandbox (curl test)

TEST phase:
  ✓ All success criteria from PLAN verified
  ✓ User story workflows executed
  ✓ Browser UI testing (if applicable)
  ✓ Performance benchmarks (if applicable)
```

**Cascade Prevention**:
- If BUILD fails: provides specific error, testing clarifies root cause
- If HOST fails: likely CORS or port config, easy to debug
- If TEST fails: success criteria tell you exactly what's broken

---

### 7. Explicit Instructions for Complex Operations

**Pattern**: Step-by-step breakdowns for non-trivial tasks

**Example** (from plan-build-host-test.md):

For the HOST step:
```
DO NOT STOP in between steps. Complete every step in the workflow before stopping.

## Step 4: Host and Expose Application
- Run `\host [sandbox_id] [PORT]`
- This sets up client and server applications in the sandbox
- Starts the server in background mode on PORT
- Retrieves the public URL using `sbx sandbox get-host`
- Validates the application is accessible with curl
- Store the public URL for the final report
- Use this as an opportunity to test the application from OUTSIDE the sandbox
- (CRITICAL) Be sure you run your final test from OUTSIDE the sandbox to validate the user's access
```

**Key Points**:
- Each step explicitly states what command to run
- Outputs to capture are bolded
- Critical requirements are emphasized
- Testing instructions are specific (OUTSIDE the sandbox, with curl)

---

### 8. Documentation Within Implementation

**Pattern**: README.md and inline docs are part of the deliverable

**Requirement** (from Step 3 in plan-build-host-test.md):
```
IMPORTANT: As you wrap up this step, be sure to document how to run the frontend,
backend, and database in the README.md at the top of your application directory.

Keep it concise:
- Describe the app
- Describe requirements
- Describe setup steps to run it
- But don't get too verbose (keep it under 100 lines)
```

**Why This Matters**:
- Next agent/engineer can immediately understand the system
- Reduces onboarding friction
- Creates accountability (if something's undocumented, it's incomplete)

---

### 9. The "Why This Works" Section (Justification Pattern)

**Pattern**: Explicitly articulate the benefits of the approach

**Example** (from very_easy_calculator.md):
```
## Why This Works

✅ Simple: Basic arithmetic only
✅ Fast: Can build in under 10 minutes
✅ Complete: Tests CRUD operations and API integration
✅ Observable: Easy to verify calculations are correct
✅ Practical: Real-world use case
```

**Key Insight**: The specification includes its own validation. If the "why this works" section can't be written convincingly, the spec is probably wrong.

---

## Adoption Strategy for Flourisha

### Phase 1: E2B Integration (Current)

**Implementation**:
1. ✅ E2B API key added to `.env`
2. Copy agent-sandbox-skill to Flourisha projects
3. Create wrapper skill with disler's prompt patterns
4. Test with simple sandbox tasks
5. Document learnings

**Timeline**: This session

**Success Criteria**:
- ✅ E2B API key configured
- [ ] Simple Python execution in sandbox
- [ ] Full-stack calculator app built in E2B (proof of concept)
- [ ] Public URL accessible and tested

### Phase 2: Docker Optimization (Deferred)

**Rationale**: E2B validates the approach; Docker optimizes costs
- E2B hourly cost: $0.13-0.44/hr depending on template
- Docker: Free (use existing Contabo infrastructure)
- Plan: Migrate to Docker once workflow proven

**Timeline**: Next quarter (after Phase 1 validation)

---

## Key Files to Reference

| File | Purpose | Key Learning |
|------|---------|---------------|
| `very_easy_calculator.md` | Spec template example | Detailed section structure; success criteria as checkboxes |
| `plan-build-host-test.md` | Workflow orchestration | Sequential phases; output capture; explicit instructions |
| `SKILL.md` | E2B integration guide | Template tiers; CLI commands; prerequisites |

---

## Summary Table: Disler's 9 Principles

| # | Principle | Implementation | Flourisha Adoption |
|---|-----------|-----------------|-------------------|
| 1 | Specification Template | 8+ detailed sections | Adopt for all agent tasks |
| 2 | Sequential Workflows | Plan→Build→Host→Test | Use for complex projects |
| 3 | Output Capture | Name & remember artifacts | Use between agent steps |
| 4 | Standardized Stack | Pre-built E2B templates | Use fullstack-vue-fastapi-node22 |
| 5 | E2B Integration | Sandbox CLI with templates | Phase 1 implementation |
| 6 | Multi-Step Validation | Test at each phase | Use for QA workflow |
| 7 | Explicit Instructions | Step-by-step + critical callouts | Use for complex agent tasks |
| 8 | Documentation | README.md as deliverable | Require for all builds |
| 9 | "Why This Works" | Justification pattern | Use in spec sections |

---

## Next Steps

1. Create `/root/.claude/skills/agent-sandbox-wrapper/` with Flourisha-specific patterns
2. Implement sample task: "Build calculator app in E2B sandbox"
3. Document Phase 1 completion and learnings
4. Prepare Phase 2 Docker migration plan

