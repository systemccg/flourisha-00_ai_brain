---
name: clickup-tasks
description: ClickUp task management for autonomous coding projects. USE WHEN user says 'create project tasks', 'check clickup', 'task progress', 'update clickup', 'manage tasks', 'work autonomously', 'build long-term', OR needs task tracking for coding projects.
triggers:
  - clickup
  - task management
  - autonomous coding
  - work autonomously
  - build long-term
---

# ClickUp Task Management

Manage coding projects with ClickUp as the source of truth for task tracking.

## Architecture Overview

```
ClickUp: Project Central / Flourisha
├── 🧠 AI Brain Development     ← Flourisha infrastructure (LIST: 901112608092)
├── 💡 Idea Scratchpad          ← Ideas, YouTube links, pre-project (LIST: 901112609506)
└── 📁 {Project Lists}          ← One per formal project (created on demand)
```

**Centralized Paths (AI Brain is source of truth):**

```
/root/flourisha/00_AI_Brain/
├── plans/              ← Plan mode files (symlink: ~/.claude/plans)
├── scratchpad/         ← Ideas & scratch work (symlink: ~/.claude/scratchpad)
├── skills/clickup-tasks/
└── ...
```

**Directory-to-List Mapping:**

| Working Directory | ClickUp List | Behavior |
|-------------------|--------------|----------|
| `/root/flourisha/00_AI_Brain/scratchpad/*` | Idea Scratchpad | Quick capture, ideas, YouTube analysis |
| `/root/flourisha/00_AI_Brain/*` | AI Brain Development | Infrastructure tasks |
| `/root/flourisha/00_AI_Brain/plans/*` | Idea Scratchpad | Plans sync as ideas until graduated |
| `/root/flourisha/01f_Flourisha_Projects/{name}/*` | `{name}` list | Create if missing |
| Other directories | None | Explicit trigger only |

**Symlinks for Claude Code compatibility:**
- `~/.claude/plans` → `/root/flourisha/00_AI_Brain/plans`
- `~/.claude/scratchpad` → `/root/flourisha/00_AI_Brain/scratchpad`

---

## Idea Scratchpad Workflow

Ideas flow from various sources into the Idea Scratchpad list:

```
Inbox Feed ──┐
             ├──► Idea Scratchpad ──► Formal Project (graduates)
Idea Incubator ─┘        │
                         └──► Archived (abandoned)
```

**Idea Tags:**
- `idea` (gray) - Raw concept captured
- `youtube` (red) - Requires YouTube video analysis
- `needs-research` (purple) - Requires investigation before proceeding
- `ready-to-graduate` (green) - Validated, ready for formal project
- `stale` (brown) - Idle >30 days, needs review

**Processing YouTube Ideas:**
When an idea includes a YouTube link:
1. Analyze the video content using transcripts/summaries
2. Extract key insights relevant to why it was saved
3. Update task description with findings
4. Tag appropriately (`functional`, `infrastructure`, etc.)
5. Recommend: graduate to project OR archive

**Graduation Criteria:**
An idea is ready to graduate when:
- Clear scope and deliverables defined
- 5+ subtasks identified
- Priority 1-2 assigned
- Tagged `ready-to-graduate`

---

## Quick Reference

| Action | Command |
|--------|---------|
| Check workspace | `mcp__clickup__get_workspace_hierarchy` |
| List tasks | `mcp__clickup__get_tasks` |
| Create task | `mcp__clickup__create_task` |
| Update status | `mcp__clickup__update_task` |
| Add comment | `mcp__clickup__create_task_comment` |

## MCP Server Configuration

The ClickUp MCP server is loaded on-demand. To use ClickUp tools, ensure the MCP server is active:

```json
{
  "clickup": {
    "command": "npx",
    "args": ["-y", "@taazkareem/clickup-mcp-server@latest"],
    "env": {
      "CLICKUP_API_KEY": "${CLICKUP_API_KEY}",
      "CLICKUP_TEAM_ID": "${CLICKUP_TEAM_ID}"
    }
  }
}
```

## Available ClickUp MCP Tools

### Workspace & Navigation
- `mcp__clickup__get_workspace_hierarchy` - List spaces, folders, lists
- `mcp__clickup__get_workspace_members` - List team members
- `mcp__clickup__find_member_by_name` - Find member by name/email

### Task Management
- `mcp__clickup__create_task` - Create single task
- `mcp__clickup__create_bulk_tasks` - Create multiple tasks efficiently
- `mcp__clickup__get_task` - Get single task details
- `mcp__clickup__get_tasks` - List tasks with filters (status, priority)
- `mcp__clickup__update_task` - Update task status/priority/assignee
- `mcp__clickup__delete_task` - Delete a task
- `mcp__clickup__move_task` - Move task to different list
- `mcp__clickup__duplicate_task` - Duplicate a task

### Comments & Attachments
- `mcp__clickup__get_task_comments` - Read task comments
- `mcp__clickup__create_task_comment` - Add comment to task
- `mcp__clickup__attach_task_file` - Attach file to task

### Lists & Folders
- `mcp__clickup__create_list` - Create new list in space
- `mcp__clickup__get_list` - Get list details
- `mcp__clickup__update_list` - Update list properties
- `mcp__clickup__create_folder` - Create folder in space
- `mcp__clickup__create_list_in_folder` - Create list inside folder

### Tags
- `mcp__clickup__get_space_tags` - List available tags
- `mcp__clickup__create_space_tag` - Create new tag
- `mcp__clickup__add_tag_to_task` - Add tag to task
- `mcp__clickup__remove_tag_from_task` - Remove tag from task

### Time Tracking
- `mcp__clickup__start_time_tracking` - Start timer
- `mcp__clickup__stop_time_tracking` - Stop timer
- `mcp__clickup__get_task_time_entries` - Get time entries

---

## Workflows

### Quick Operations

**Check task progress:**
```
1. mcp__clickup__get_tasks with list_id, filter by status
2. Count tasks by status: to do / in progress / complete
3. Report summary
```

**Update task status:**
```
1. mcp__clickup__get_task to verify task exists
2. mcp__clickup__update_task with new status
3. mcp__clickup__create_task_comment with update notes
```

### Autonomous Coding Mode

When user says "work autonomously on X" or "build this long-term":

1. **Initialize Project** (see `workflows/initialize-project.md`)
   - Read project specification
   - Create ClickUp list for project
   - Create 50 detailed tasks covering all features
   - Create META task for session tracking
   - Save `.clickup_project.json` marker

2. **Coding Sessions** (see `workflows/coding-session.md`)
   - Read `.clickup_project.json` for context
   - Check META task comments for previous session notes
   - Find highest-priority "to do" task
   - Update to "in progress"
   - Implement and test feature
   - Add implementation comment
   - Mark "complete"
   - Update META with session summary

---

## Task Status Workflow

```
to do → in progress → complete
          ↑               │
          └───────────────┘ (if regression found)
```

**Status Values (Project Central workspace):**
- `--` - Open/To do (default open status)
- `in progress` - Currently being worked on
- `waiting for` - Blocked/waiting on something
- `on hold` - Paused
- `in review` - Ready for review
- `done` - Completed
- `Closed` - Archived

**Priority Values:**
- 1 = Urgent (foundational, blocking)
- 2 = High (core features)
- 3 = Normal (secondary features)
- 4 = Low (polish, nice-to-have)

**Category Tags:**
- `functional` - Feature implementation (green: #4CAF50)
- `infrastructure` - Setup, config, tooling (blue: #2196F3)
- `style` - UI/UX, visual changes (purple: #9C27B0)

**Assignment Workflow:**

| Assignee | User ID | Use When |
|----------|---------|----------|
| **Flourisha System** | `87375090` | AI should work on this task |
| **Greg Wasmuth** | `12782467` | Needs human review/action |

- Tasks assigned to Flourisha = AI work queue
- Tasks assigned to Greg + status `in review` = needs human attention
- Add relevant category tag to all tasks

---

## Task Template

When creating tasks for coding projects, use `markdown_description` field for proper formatting:

**API Field:** Use `markdown_description` instead of `description` for rich text rendering.

```json
{
  "name": "[Category] - Feature name",
  "markdown_description": "## Feature Description\n\n[Brief description]\n\n## Category\n\n`functional` | `style` | `infrastructure`\n\n## Test Steps\n\n1. Navigate to [page]\n2. [Action]\n3. Verify [result]\n\n## Acceptance Criteria\n\n- [ ] Criterion 1\n- [ ] Criterion 2",
  "priority": 2,
  "status": "--"
}
```

**Rendered in ClickUp:**

```markdown
## Feature Description

[Brief description of what this feature does]

## Category

`functional` | `style` | `infrastructure`

## Test Steps

1. Navigate to [page/location]
2. [Specific action to perform]
3. Verify [expected result]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

---

## META Task

Every project should have a META task titled `[META] Project Progress Tracker`:

```markdown
## Project Overview
[Project name and brief description]

## Session Tracking
This task is used for session handoff between coding agents.
Each session should add a comment summarizing progress.

## Key Milestones
- [ ] Project setup complete
- [ ] Core infrastructure working
- [ ] Primary features implemented
- [ ] All features complete
- [ ] Polish and refinement done
```

---

## Project State File

After initialization, save `.clickup_project.json` in project directory:

```json
{
  "initialized": true,
  "created_at": "2025-12-08T12:00:00Z",
  "space_id": "12345678",
  "list_id": "901234567",
  "list_name": "Project Name",
  "meta_task_id": "abc123",
  "total_tasks": 50,
  "notes": "Project initialized"
}
```

---

## Environment Variables

Stored in `/root/.claude/.env`:

```bash
CLICKUP_API_KEY=pk_...      # Personal API token
CLICKUP_TEAM_ID=8655078     # Team/workspace ID
```

---

## Project Graduation Workflow

When an idea is ready to become a formal project:

### 1. Create Project Structure

```bash
# Create project folder
mkdir -p /root/flourisha/01f_Flourisha_Projects/{project-name}

# Initialize with README
echo "# {Project Name}\n\nDescription..." > /root/flourisha/01f_Flourisha_Projects/{project-name}/README.md
```

### 2. Create ClickUp List

```bash
# API: Create list in Flourisha folder
POST /api/v2/folder/90117368142/list
{"name": "{Project Name}"}
```

### 3. Expand to 50 Tasks

Break the idea into comprehensive tasks covering:
- Infrastructure/setup (Priority 1)
- Core features (Priority 2)
- Secondary features (Priority 3)
- Polish/edge cases (Priority 4)

### 4. Create META Task

Title: `[META] {Project Name} Progress Tracker`

### 5. Save Project Marker

Create `.clickup_project.json` in project folder:

```json
{
  "initialized": true,
  "created_at": "2025-12-08T12:00:00Z",
  "list_id": "{new_list_id}",
  "list_name": "{Project Name}",
  "meta_task_id": "{meta_task_id}",
  "graduated_from": "{original_idea_task_id}",
  "total_tasks": 50
}
```

### 6. Close Original Idea

Update original idea task:
- Status: `done`
- Add comment: "Graduated to project: {Project Name} (List: {list_id})"

---

## Related Resources

- Workflow templates: `workflows/`
- Task templates: `templates/`
- Example specs: `examples/`
- Configuration: `reference/clickup_config.py`
- ClickUp MCP docs: https://github.com/taazkareem/clickup-mcp-server
