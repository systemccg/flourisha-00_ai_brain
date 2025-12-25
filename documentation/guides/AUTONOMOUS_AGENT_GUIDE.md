# Getting Started with the ClickUp Autonomous Agent

**Guide for running autonomous coding sessions on Flourisha.**

*Last Updated: 2025-12-19*

---

## Quick Start

```bash
cd /root/flourisha/00_AI_Brain/agents/clickup-autonomous
source ~/.claude/.env
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api
```

**Critical:** Always use `--project flourisha` to use Flourisha-specific prompts.

---

## How It Works

### Two-Agent Pattern

The harness uses two types of agents:

| Agent | When Used | Purpose |
|-------|-----------|---------|
| **Initializer** | First session | Sets up ClickUp tasks, project structure |
| **Coding Agent** | Subsequent sessions | Implements features, marks tasks complete |

### Prompt Selection

```
--project flourisha
       ↓
set_active_project("flourisha")
       ↓
Loads: flourisha_initializer_prompt.md  OR  flourisha_coding_prompt.md
       ↓
Agent reads: SYSTEM_SPEC.md, AUTONOMOUS_TASK_SPEC.md
```

**Without `--project flourisha`:**
- Uses generic prompts designed for new projects
- Looks for `app_spec.txt` (not Flourisha)
- Won't know about existing services

**With `--project flourisha`:**
- Uses Flourisha-specific prompts
- Reads canonical documentation
- Knows to WRAP existing services, not rewrite them

---

## Prerequisites

### Environment Variables

Required in `~/.claude/.env`:

```bash
# Claude Code
CLAUDE_CODE_OAUTH_TOKEN=your-token-here

# ClickUp
CLICKUP_API_KEY=pk_xxxxxxxxxxxxx
CLICKUP_TEAM_ID=12345678

# Optional but recommended
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
ANTHROPIC_API_KEY=...
```

### Get OAuth Token

```bash
claude setup-token
```

### Get ClickUp API Key

1. Go to: https://app.clickup.com/settings/apps
2. Generate Personal API Token
3. Find Team ID in your workspace URL: `https://app.clickup.com/12345678/`

---

## Command Reference

### Basic Usage

```bash
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api
```

### All Options

| Flag | Default | Description |
|------|---------|-------------|
| `--project` | None | Project type for prompts (use `flourisha`) |
| `--project-dir` | `./autonomous_demo_project` | Working directory for the agent |
| `--model` | `claude-opus-4-5-20251101` | Claude model to use |
| `--max-iterations` | Unlimited | Limit agent iterations (for testing) |

### Examples

```bash
# Standard Flourisha session
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api

# Limited iterations for testing
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api --max-iterations 5

# Use Sonnet for faster iterations
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api --model claude-sonnet-4-5-20250929
```

---

## Project Files

### Prompts (in `prompts/`)

| File | Purpose |
|------|---------|
| `flourisha_initializer_prompt.md` | First session setup instructions |
| `flourisha_coding_prompt.md` | Coding session workflow |
| `flourisha_spec.txt` | Quick reference (points to SYSTEM_SPEC.md) |
| `initializer_prompt.md` | Generic (non-Flourisha) initializer |
| `coding_prompt.md` | Generic (non-Flourisha) coding |

### Documentation (Flourisha prompts point here)

| Document | Location |
|----------|----------|
| **SYSTEM_SPEC.md** | `documentation/SYSTEM_SPEC.md` |
| **AUTONOMOUS_TASK_SPEC.md** | `documentation/AUTONOMOUS_TASK_SPEC.md` |
| **FRONTEND_FEATURE_REGISTRY.md** | `documentation/FRONTEND_FEATURE_REGISTRY.md` |

### Generated Files

| File | Purpose |
|------|---------|
| `.clickup_project.json` | Stores ClickUp list/task IDs for session continuity |

---

## Session Workflow

### First Session (Initializer)

1. Reads `flourisha_initializer_prompt.md`
2. Creates ClickUp list "Flourisha API Backend"
3. Imports 75 tasks from `AUTONOMOUS_TASK_SPEC.md`
4. Creates META task for session tracking
5. Saves `.clickup_project.json`
6. Optionally starts implementation

### Subsequent Sessions (Coding Agent)

1. Reads `flourisha_coding_prompt.md`
2. Loads `.clickup_project.json` for ClickUp context
3. Reads META task comments for session history
4. Verifies previously completed features still work
5. Picks highest-priority "to do" task
6. Implements, tests, marks complete
7. Updates META task with session summary

---

## ClickUp Integration

### Task States

```
to do  →  in progress  →  complete
                ↑            │
                └────────────┘ (if regression found)
```

### ClickUp Python API

Uses direct REST API calls via `clickup_api.py` - no MCP server required.

**Client Location:** `/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference/clickup_api.py`

| Method | Purpose |
|--------|---------|
| `client.get_spaces()` | List spaces in workspace |
| `client.create_list(folder_id, name)` | Create new list |
| `client.get_list_tasks(list_id)` | Get tasks from list |
| `client.create_task(list_id, name, ...)` | Create single task |
| `client.create_bulk_tasks(list_id, tasks)` | Create multiple tasks |
| `client.update_task(task_id, status=...)` | Change task status |
| `client.add_comment(task_id, text)` | Add implementation notes |
| `client.get_comments(task_id)` | Read session history |

---

## Key Principles

### 1. Wrap, Don't Rewrite

Existing services in `/root/flourisha/00_AI_Brain/services/` **work**. The agent should wrap them in API endpoints, not reimplement them.

### 2. Read the Spec First

The agent is instructed to read `SYSTEM_SPEC.md` before doing anything. This ensures it understands the Five Pillars architecture, three-store knowledge system, and existing services.

### 3. Session Continuity via ClickUp

- Tasks persist across sessions
- META task comments provide session history
- `.clickup_project.json` stores IDs for quick lookup

### 4. Verify Before Building

Each coding session starts by verifying previously completed features still work. Regressions are fixed before new work.

---

## Troubleshooting

### "CLAUDE_CODE_OAUTH_TOKEN not set"

```bash
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN='your-token'
```

### "CLICKUP_API_KEY not set"

Get from https://app.clickup.com/settings/apps

### Agent uses generic prompts

Make sure you include `--project flourisha`:
```bash
python run_autonomous_agent.py --project flourisha ...
```

### Agent can't find existing services

Verify you're using `--project flourisha` which loads prompts that reference `SYSTEM_SPEC.md`.

---

## Plan File Naming Convention

Claude Code generates random names like `floofy-tumbling-tarjan.md` for plan files. **Rename them immediately** to follow this convention:

```
YYYY-MM-DD-description-of-plan.md
```

**Examples:**
- `2025-12-19-ai-brain-root-cleanup.md`
- `2025-12-18-firebase-auth-documentation.md`
- `2025-12-15-docker-migration-phase2.md`

**Why this matters:**
- Plans are stored in `documentation/plans/` (symlinked from `~/.claude/plans`)
- Descriptive names make plans searchable and understandable
- Date prefix enables chronological sorting
- Random names like "zippy-humming-allen" tell you nothing

**After creating a plan:**
```bash
# Rename immediately
mv ~/.claude/plans/silly-random-name.md ~/.claude/plans/2025-12-19-actual-description.md
```

---

## Related Documentation

- [SYSTEM_SPEC.md](../SYSTEM_SPEC.md) - Canonical system reference
- [AUTONOMOUS_TASK_SPEC.md](../AUTONOMOUS_TASK_SPEC.md) - 75 tasks by Five Pillars
- [FRONTEND_FEATURE_REGISTRY.md](../FRONTEND_FEATURE_REGISTRY.md) - Feature specifications

---

*For questions about the Flourisha system, see SYSTEM_SPEC.md*
