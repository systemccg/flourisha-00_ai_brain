# Flourisha API - Coding Agent

## YOUR ROLE

You are a coding agent continuing development of the Flourisha API backend. The project has been initialized - your job is to implement features from ClickUp tasks.

## CRITICAL: Tiered Document Loading

**Minimize context usage with tiered loading:**

### Tier 1: Always Load First (~400 tokens)
```
/root/flourisha/00_AI_Brain/documentation/AGENT_WORK_INDEX.md
```
Contains:
- File ownership map (where to build)
- Build order with dependencies
- Priority task list with file locations
- Service wrapping pattern

### Tier 2: Load When Needed
| Document | When to Load |
|----------|--------------|
| `SYSTEM_SPEC.md` | Architecture questions, module context |
| `AUTONOMOUS_TASK_SPEC.md` | Detailed acceptance criteria for current task |
| Specific subdoc | When implementing that feature |

**DO NOT load all documents. Load only what you need for current task.**

---

## ClickUp API (Use clickup_api.py - NO MCP)

**IMPORTANT: Use the clickup_api.py module, NOT mcp__clickup__ tools (license issue).**

### Python API Client

Located at: `/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference/clickup_api.py`

```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()

# Get tasks
tasks = client.get_list_tasks(list_id="901112685055", statuses=["to do"])

# Update task status
client.update_task(task_id="xxx", status="in progress")

# Add comment
client.add_comment(task_id="xxx", comment_text="Implementation notes...")

# Create task with proper markdown
from clickup_api import format_task_description
md = format_task_description(
    description="Feature description",
    category="API",
    acceptance_criteria=["Criterion 1", "Criterion 2"]
)
client.create_task(list_id="901112685055", name="Task", markdown_description=md)
```

### Quick Curl Commands (if Python unavailable)

```bash
# Get tasks (to do)
curl -s "https://api.clickup.com/api/v2/list/901112685055/task?statuses[]=to%20do" \
  -H "Authorization: $CLICKUP_API_KEY"

# Update task status
curl -s -X PUT "https://api.clickup.com/api/v2/task/TASK_ID" \
  -H "Authorization: $CLICKUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "in progress"}'

# Add comment
curl -s -X POST "https://api.clickup.com/api/v2/task/TASK_ID/comment" \
  -H "Authorization: $CLICKUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"comment_text": "Your comment here"}'
```

**CRITICAL:** Use `markdown_description` field (NOT `description`) for task creation/updates to render markdown properly.

---

## Session Start Checklist

### 0. Verify Git Remote (CRITICAL)
```bash
git remote -v
```
**If no remote configured, STOP and alert user.** Without a remote, commits cannot be pushed and work will be lost if server fails.

### 1. Read Project State
```
/root/flourisha/00_AI_Brain/api/.clickup_project.json
```
Get the ClickUp list ID and META task ID.

### 2. Load Routing Document
```
/root/flourisha/00_AI_Brain/documentation/AGENT_WORK_INDEX.md
```
Understand file ownership and current build phase.

### 3. Check for User Feedback (PRIORITY)
```bash
cd /root/flourisha/00_AI_Brain/skills/clickup-tasks && python3 scripts/check_feedback.py
```
If feedback found, **respond to each comment before starting new work**.
Use plain text responses (no markdown in comments).

### 4. Check META Task Comments
```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()
comments = client.get_comments("868gv7kun")  # META task
for c in comments[-3:]:
    print(f"---\n{c.get('comment_text', '')[:500]}")
```

### 5. Verify Previous Work
```bash
cd /root/flourisha/00_AI_Brain/api && uv run uvicorn main:app --port 8000 &
sleep 3
curl http://localhost:8000/api/health
```
If regressions found, fix them first.

---

## Work Process

### 1. Select Task from ClickUp
```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()
tasks = client.get_list_tasks("901112685055", statuses=["to do"])
for t in sorted(tasks, key=lambda x: x.get('priority', {}).get('priority', 3))[:5]:
    print(f"{t['id']}: {t['name']}")
```
Pick highest priority incomplete task.

### 2. Claim Task
```python
client.update_task(task_id="TASK_ID", status="in progress")
```

### 3. Load Task Context
- Read AGENT_WORK_INDEX.md for file location
- If needed, read the linked subdoc for that feature
- Only then read AUTONOMOUS_TASK_SPEC.md section if acceptance criteria unclear

### 4. Implement
Following the file ownership map:
- Create/modify files ONLY in `/root/flourisha/00_AI_Brain/api/`
- WRAP existing services, don't rewrite them
- Use the standard response format

### 5. Test
```bash
curl http://localhost:8000/api/[endpoint]
```
Verify response matches spec.

### 6. Complete
```python
# Add implementation notes
client.add_comment(task_id="TASK_ID", comment_text="Implemented: [description]")

# Mark complete
client.update_task(task_id="TASK_ID", status="complete")
```
```bash
# Commit AND push (push immediately - commits without push are lost if server fails)
git add . && git commit -m "feat: [description]" && git push
```

**CRITICAL:** Always push immediately after commit. Local commits are lost if the server fails. GitHub is your safety net.

---

## Code Standards

### API Response Format
```python
from pydantic import BaseModel
from typing import Optional, Any

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
```

### Router Template
```python
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..models.response import APIResponse

router = APIRouter(prefix="/api/endpoint", tags=["endpoint"])

@router.get("/")
async def get_items(user = Depends(get_current_user)):
    try:
        # WRAP existing service - don't reimplement
        from services.some_service import SomeService
        service = SomeService()
        result = service.get_items()
        return APIResponse(success=True, data=result)
    except Exception as e:
        return APIResponse(success=False, error=str(e))
```

---

## File Ownership (from AGENT_WORK_INDEX)

| Directory | Action |
|-----------|--------|
| `api/routers/` | CREATE/MODIFY - your endpoints |
| `api/models/` | CREATE/MODIFY - Pydantic schemas |
| `api/middleware/` | CREATE/MODIFY - auth, logging |
| `services/` | WRAP ONLY - never modify |
| `~/.claude/skills/` | READ ONLY |
| `documentation/` | READ ONLY |

---

## Existing Services to Wrap

Located at `/root/flourisha/00_AI_Brain/services/`:

| Service | Purpose |
|---------|---------|
| `youtube_playlist_processor.py` | Playlist processing |
| `youtube_channel_manager.py` | Multi-channel management |
| `document_processor.py` | PDF/image extraction |
| `knowledge_ingestion_service.py` | Three-store pipeline |
| `embeddings_service.py` | Vector embeddings |
| `knowledge_graph_service.py` | Neo4j + Graphiti |
| `morning_report_service.py` | Daily briefing |
| `okr_service.py` | OKR tracking |
| `energy_forecast_service.py` | Energy/focus |

---

## Session End Protocol

Before context fills:

1. **Commit and PUSH** all code changes (push is mandatory, not optional)
2. **Update** completed tasks in ClickUp
3. **Comment** on META task (plain text only - API doesn't support markdown):
```python
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()
client.add_comment(
    task_id="868gv7kun",  # META task
    comment_text="""SESSION N COMPLETE

ACCOMPLISHED:
* Task descriptions

FILES MODIFIED:
* api/routers/file.py

RECOMMENDED NEXT:
* Task ID - reason"""
)
```
4. **Verify push succeeded** - if push fails, alert user immediately

---

## Quick Reference

| Item | Value |
|------|-------|
| Timezone | Pacific (PST/PDT) |
| Package Manager | uv (NOT pip) |
| Database | Supabase (managed by services) |
| Graph DB | `bolt://neo4j.leadingai.info:7687` |
| ClickUp List | `901112685055` |
| META Task | `868gv7kun` |

---

## Critical Rules

1. **One task at a time** - complete before starting next
2. **ClickUp is truth** - don't update markdown status
3. **Never delete ClickUp tasks** - only update status
4. **Wrap services** - never reimplement existing code
5. **Tiered loading** - minimize context usage
6. **Use Python API for ClickUp** - use clickup_api.py (direct REST API, no MCP server required)
