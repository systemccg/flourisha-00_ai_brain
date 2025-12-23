# Agent Sandbox Quick Start Guide

**Version**: 1.0
**Date**: 2025-12-04
**Status**: ✅ Ready to Use

---

## What This Is

A complete system for running Flourisha agent tasks in isolated E2B sandboxes, using disler's proven prompt engineering patterns.

---

## Quick Examples

### Example 1: Run Python Code in Sandbox

```bash
# 1. Initialize sandbox (captures ID)
source ~/.local/bin/env
export E2B_API_KEY="e2b_4f555888358be28ebfb1d67f81dc99b471d75148"
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/

SANDBOX_ID=$(uv run sbx init --timeout 3600 --name my-test | grep "Sandbox ID:" | awk '{print $NF}')

# 2. Execute Python
uv run sbx exec "$SANDBOX_ID" 'python -c "print(\"Hello from sandbox!\")"'

# 3. Clean up (manual, or auto-terminates after 1 hour)
# uv run sbx sandbox kill "$SANDBOX_ID"
```

### Example 2: Build Full-Stack App

**Using Agent** (recommended):
```bash
# Ask agent to build with disler patterns
"Build a calculator web app with history"

# Agent will:
# 1. Create detailed specification
# 2. Init sandbox
# 3. Build frontend + backend + database
# 4. Expose public URL
# 5. Test everything
# 6. Return working app
```

**Manual Steps**:
```bash
# 1. Plan phase
\flourisha-sandbox:plan "Build calculator"
# Outputs: specification file

# 2. Build phase
\flourisha-sandbox:build path/to/spec
# Outputs: working app in sandbox

# 3. Host phase
\flourisha-sandbox:host [sandbox_id]
# Outputs: public URL

# 4. Test phase
\flourisha-sandbox:test [sandbox_id] [public_url]
# Outputs: validation report
```

---

## Key Commands

### Initialize Sandbox
```bash
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/
uv run sbx init --timeout 3600 --name "my-task-$(date +%s)"
```

**Output**: `Sandbox ID: abc123...`

### Execute Command
```bash
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/
uv run sbx exec [SANDBOX_ID] "python script.py"
```

### List Files
```bash
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/
uv run sbx files ls [SANDBOX_ID] /path
```

### Upload/Download
```bash
# Upload local file to sandbox
uv run sbx files upload [SANDBOX_ID] local.py remote/script.py

# Download from sandbox
uv run sbx files download [SANDBOX_ID] remote/output.txt local.txt
```

### Get Public URL
```bash
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/
uv run sbx sandbox get-host [SANDBOX_ID]
```

### Terminate Sandbox (Manual)
```bash
cd ~/.claude/skills/agent-sandboxes/sandbox_cli/
uv run sbx sandbox kill [SANDBOX_ID]
```

---

## Workflow: The 4 Phases

### Phase 1: PLAN
- Create detailed specification
- Define success criteria
- Document technical requirements
- **Output**: Specification file (e.g., `spec.md`)

### Phase 2: BUILD
- Initialize E2B sandbox
- Implement from specification
- Run validation commands
- **Output**: Working application + sandbox ID

### Phase 3: HOST
- Start frontend and backend
- Generate public URL
- Test from outside sandbox
- **Output**: Public URL (e.g., `https://sandbox-123.e2b.host`)

### Phase 4: TEST
- Run comprehensive tests
- Browser UI validation
- Verify all success criteria
- **Output**: Pass/fail report

---

## Important Constraints

| Limit | Value | Impact |
|-------|-------|--------|
| Max timeout | 3600 seconds (1 hour) | Plan tasks to fit 1 hour or extend lifetime |
| Max containers | Account dependent | Monitor usage, clean up old sandboxes |
| Storage | Account dependent | Don't store large files |
| Network | Public URLs only | All network communication goes through E2B |

---

## Understanding Output Capture

Disler's approach: **name artifacts between steps, store in context**

Example:

```
Step 1: Init sandbox
  CAPTURED: sandbox_id = "abc123def456"

Step 2: Build app
  USE: sandbox_id (from step 1)
  CAPTURED: build_status = "success"

Step 3: Host app
  USE: sandbox_id (from step 1)
  CAPTURED: public_url = "https://abc123.e2b.host"

Step 4: Test app
  USE: public_url (from step 3)
  CAPTURED: test_results = "all passed"
```

---

## Cost

**Phase 1 (E2B)**:
- $0.13-0.44 per sandbox per hour
- Typical task: 1 hour = $0.13-0.44
- Very cost-effective for development

**Phase 2 (Docker)** - Coming later:
- $0 per container (uses existing Contabo infrastructure)
- Unlimited runtime
- Better for production

---

## Troubleshooting

### `401: Unauthorized`
**Problem**: API key not passed to uv
**Solution**:
```bash
export E2B_API_KEY="e2b_4f555888358be28ebfb1d67f81dc99b471d75148"
```

### `Timeout cannot be greater than 1 hour`
**Problem**: Used 43200 seconds (12 hours)
**Solution**: Use 3600 or less
```bash
uv run sbx init --timeout 3600
```

### `Template not found`
**Problem**: Tried custom template not on account
**Solution**: Don't use `--template` flag (uses default)
```bash
uv run sbx init --timeout 3600 --name my-task
```

### Sandbox doesn't respond
**Problem**: Timeout expired (1 hour)
**Solution**: Create new sandbox or extend lifetime
```bash
# Extend lifetime by 1 hour
uv run sbx sandbox extend-lifetime [SANDBOX_ID] 1
```

---

## Learning More

### Read These Docs (In Order)

1. **DISLER_PROMPT_ENGINEERING_PRINCIPLES.md** (2,000 words)
   - Understand the patterns
   - Why they work

2. **flourisha-sandbox SKILL.md** (600+ lines)
   - How to use the wrapper skill
   - Template options
   - Complete workflow

3. **E2B_PHASE1_TEST_REPORT.md** (1,500 words)
   - Test results and evidence
   - Technical findings
   - What we learned

4. **PHASE2_DOCKER_MIGRATION_PLAN.md** (2,000 words)
   - Future optimization plan
   - Cost savings
   - Timeline

### Example Specifications

Location: `/tmp/agent-sandbox-skill/prompts/full_stack/sonnet/very_easy_calculator.md`

This is disler's calculator specification - study it to understand how to write specifications for your own tasks.

### Cookbook Examples

Location: `~/.claude/skills/agent-sandboxes/cookbook/`

Real examples of sandboxes being used.

---

## Getting Help

### If Something Breaks

1. Check sandbox status: `uv run sbx sandbox get-info [SANDBOX_ID]`
2. Review error messages carefully
3. Check troubleshooting guide above
4. See full technical report: `E2B_PHASE1_TEST_REPORT.md`

### If You Need to Build Something

1. Create a detailed specification following disler's pattern
2. Use the 4-phase workflow (Plan→Build→Host→Test)
3. Capture outputs between phases
4. Validate at each step

### If You Want to Understand More

Read: `/root/flourisha/00_AI_Brain/documentation/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md`

This explains why the patterns work and how to think about agent tasks.

---

## Next: Build Calculator App

Ready to try it out? Follow these steps:

1. **Read the spec**: `/tmp/agent-sandbox-skill/prompts/full_stack/sonnet/very_easy_calculator.md`

2. **Ask an agent to build it**:
   ```
   "Build a simple calculator app with calculation history using disler's patterns
    and E2B sandbox. Follow the spec at very_easy_calculator.md exactly."
   ```

3. **Verify it works**:
   - Check all 12 success criteria
   - Test public URL from outside sandbox
   - Verify database persistence

4. **Document learnings**: What worked? What took longer than expected?

---

## Configuration Reference

### Environment Variables

Required:
```bash
export E2B_API_KEY="e2b_4f555888358be28ebfb1d67f81dc99b471d75148"
```

Optional:
```bash
export FLOURISHA_SANDBOX_TEMPLATE="fullstack-vue-fastapi-node22"
export FLOURISHA_SANDBOX_TIMEOUT="3600"
```

### Key Locations

```
Skills:
  ~/.claude/skills/flourisha-sandbox/           # Wrapper skill
  ~/.claude/skills/agent-sandboxes/             # CLI interface

Docs:
  ~/flourisha/00_AI_Brain/documentation/        # All documentation

Examples:
  /tmp/agent-sandbox-skill/prompts/             # disler's examples

Scripts:
  ~/.claude/skills/agent-sandboxes/sandbox_cli/ # CLI binary
```

---

## Summary

✅ **You now have**:
- Working E2B sandbox infrastructure
- Disler's proven prompt patterns
- Complete workflow system (Plan→Build→Host→Test)
- Zero-cost development with Phase 2 Docker coming later

🎯 **Next steps**:
1. Build calculator proof-of-concept
2. Validate disler's patterns work for Flourisha
3. Create specifications for real features
4. Plan Phase 2 Docker migration

💡 **Key insight**: Specification quality determines success. Spend time on specs (Phase 1 of workflow) and builds become trivial (Phase 2).

---

**Ready to build something awesome? Start with the calculator!**

