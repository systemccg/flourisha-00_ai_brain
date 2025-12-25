# Flourisha API - Initializer Agent

## YOUR ROLE

You are initializing the Flourisha API backend project. This is NOT a greenfield build - you're creating an API layer on top of existing Python services.

**IMPORTANT:** ClickUp tasks have already been created from AUTONOMOUS_TASK_SPEC.md by the harness. Your job is to set up the project structure and start working.

## CRITICAL: Tiered Document Loading

**Load documents in this order to minimize context usage:**

### Tier 1: Always Load First (~400 tokens)
```
/root/flourisha/00_AI_Brain/documentation/AGENT_WORK_INDEX.md
```
This is your routing document. It tells you:
- File ownership (where to build)
- Build order (dependencies)
- Priority tasks with file locations
- Service wrapping pattern

### Tier 2: Load for Architecture Context (on-demand)
```
/root/flourisha/00_AI_Brain/documentation/SYSTEM_SPEC.md
```
Read ONLY the sections you need:
- "Executive Summary" for vision
- "Module: [X]" for specific pillar context

### Tier 3: Load On-Demand (when implementing specific feature)
- Subdocs linked from AGENT_WORK_INDEX
- `AUTONOMOUS_TASK_SPEC.md` for detailed acceptance criteria

**DO NOT load all documents at once. This wastes context.**

## Setup Tasks

### 1. Read AGENT_WORK_INDEX.md
Start here. Understand file ownership and build order.

### 2. Verify ClickUp Tasks Exist
The harness has already created tasks from AUTONOMOUS_TASK_SPEC.md.

Verify via Python API:
```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()
tasks = client.get_list_tasks("901112685055")
print(f"Found {len(tasks)} tasks")
```

You should see 75 tasks organized by priority. If not, alert the user.

### 3. Read .clickup_project.json
```
/root/flourisha/00_AI_Brain/api/.clickup_project.json
```
This contains your META task ID and project configuration.

### 4. Create API Directory Structure (if not exists)

```bash
mkdir -p /root/flourisha/00_AI_Brain/api/{routers,models,services,middleware}
```

### 5. Create Starter Files (if not exists)

**init.sh:**
```bash
#!/bin/bash
cd /root/flourisha/00_AI_Brain/api
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**pyproject.toml:** FastAPI + dependencies

**main.py:** Basic FastAPI app with health endpoint

### 6. Update META Task
Add a comment to the META task noting initialization is complete:
```python
client.add_comment("868gv7kun", "Initialization complete - API structure created")
```

### 7. Begin First Task
Start with Task 2.1 (Unified Search API) - it has no dependencies.

Use the workflow:
```python
# 1. Set status "in progress"
client.update_task(task_id, status="in progress")

# 2. Implement the feature
# 3. Test with curl

# 4. Add implementation notes
client.add_comment(task_id, "Implementation notes...")

# 5. Set status "complete"
client.update_task(task_id, status="done")
```

## Key Principles

1. **Tasks already exist** - Don't create new tasks, work from the list
2. **WRAP don't rewrite** - Services exist at `/root/flourisha/00_AI_Brain/services/`
3. **Single source of truth** - ClickUp for status, not markdown
4. **File ownership** - Only modify files in `api/` directory
5. **Tiered loading** - Start lean, load more only when needed

## Session End

Before context fills:
1. Commit all work
2. Update META task with session summary
3. Note recommended next tasks in META comment

## Success Criteria

- [ ] AGENT_WORK_INDEX.md read and understood
- [ ] ClickUp tasks verified (75 tasks from spec)
- [ ] API directory structure exists
- [ ] init.sh, pyproject.toml, main.py created
- [ ] Health endpoint working at `/api/health`
- [ ] At least one Priority 1-2 task completed
