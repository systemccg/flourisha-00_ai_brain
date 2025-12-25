# ClickUp Autonomous Agent

**Location:** `/root/flourisha/00_AI_Brain/agents/clickup-autonomous/`

An autonomous coding agent that uses **Claude Max subscription** (not API tokens) and **ClickUp** for task management. Part of the Flourisha AI Brain infrastructure.

*Originally forked from [coleam00/Linear-Coding-Agent-Harness](https://github.com/coleam00/Linear-Coding-Agent-Harness)*

## Key Features

- **Uses Claude Max subscription** - No API tokens needed, leverages your Claude Code subscription via OAuth
- **ClickUp integration** - Tasks managed in ClickUp instead of Linear, fully editable in ClickUp UI
- **Two-agent pattern** - Initializer agent sets up project, coding agents implement features
- **Stateless sessions** - Each session has fresh context, ClickUp is the source of truth
- **Browser verification** - All features verified via Puppeteer automation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              CLICKUP CODING AGENT HARNESS                       │
├─────────────────────────────────────────────────────────────────┤
│  Claude Max Subscription ──► Claude Code SDK (Python)           │
│                                     │                           │
│              ┌──────────────────────┼──────────────────┐        │
│              ▼                      ▼                  ▼        │
│      ClickUp Python API     Filesystem Tools    Puppeteer MCP   │
│      (REST via clickup_api) (Read/Write/Edit)   (Browser test)  │
│              │                                                  │
│              ▼                                                  │
│      ClickUp Workspace                                          │
│      ├── Space                                                  │
│      │   └── List (Your Project)                               │
│      │       ├── [META] Progress Tracker                       │
│      │       ├── Task 1: Feature X (to do)                     │
│      │       ├── Task 2: Feature Y (in progress)               │
│      │       └── Task 3: Feature Z (complete)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Claude Code CLI** installed with active subscription (Claude Max/Pro)
2. **ClickUp account** with API access
3. **Node.js 18+** (for Puppeteer MCP server)
4. **Python 3.11+**

## Setup

### 1. Install Claude Code CLI and get OAuth token

```bash
# Install Claude Code CLI (if not already installed)
npm install -g @anthropic-ai/claude-code

# Generate OAuth token for SDK usage
claude setup-token
```

### 2. Get your ClickUp credentials

1. **API Key**: Go to https://app.clickup.com/settings/apps and create a new API token
2. **Team ID**: Found in your ClickUp URL - e.g., `https://app.clickup.com/12345678/` → Team ID is `12345678`

### 3. Set environment variables

```bash
export CLAUDE_CODE_OAUTH_TOKEN='sk-ant-oat01-...'  # From claude setup-token
export CLICKUP_API_KEY='pk_...'                    # From ClickUp settings
export CLICKUP_TEAM_ID='12345678'                  # From ClickUp URL
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start a new project

```bash
python autonomous_agent_demo.py --project-dir ./my_app
```

### Continue an existing project

```bash
# Just run the same command - it detects existing .clickup_project.json
python autonomous_agent_demo.py --project-dir ./my_app
```

### Limit iterations (for testing)

```bash
python autonomous_agent_demo.py --project-dir ./my_app --max-iterations 3
```

### Use a different model

```bash
python autonomous_agent_demo.py --project-dir ./my_app --model claude-sonnet-4-5-20250929
```

## How It Works

### Session 1: Initialization

The initializer agent:
1. Reads `app_spec.txt` (your project specification)
2. Creates a ClickUp List for the project
3. Creates 50 detailed tasks covering all features
4. Creates a META task for session handoff
5. Sets up `init.sh`, git repo, and project structure
6. Saves `.clickup_project.json` marker file

### Session 2+: Coding

Each coding agent session:
1. Reads `.clickup_project.json` for ClickUp context
2. Checks META task comments for previous session context
3. Verifies previously completed features still work
4. Claims highest-priority "to do" task
5. Implements and tests the feature via Puppeteer
6. Adds implementation comment and marks "complete"
7. Updates META task with session summary

## ClickUp Task Management

### You Can Edit Tasks in ClickUp!

Unlike the Linear version, this harness is designed for bidirectional sync:
- **View progress** in ClickUp dashboard
- **Add/edit tasks** directly in ClickUp UI
- **Prioritize work** by adjusting task priorities
- **Add notes** via comments (agents read these!)

### Task Status Workflow

```
to do → in progress → complete
          ↑               │
          └───────────────┘ (if regression found)
```

### Task Structure

Each task includes:
- **Name**: Brief feature description
- **Description**: Feature details, test steps, acceptance criteria
- **Priority**: 1 (urgent) to 4 (low)
- **Status**: to do / in progress / complete
- **Comments**: Implementation notes, session handoffs

## Project Files

| File | Purpose |
|------|---------|
| `autonomous_agent_demo.py` | Main entry point |
| `agent.py` | Session orchestration |
| `client.py` | Claude SDK + MCP configuration |
| `clickup_config.py` | ClickUp constants |
| `progress.py` | Progress tracking utilities |
| `prompts/initializer_prompt.md` | First session instructions |
| `prompts/coding_prompt.md` | Continuation session instructions |
| `prompts/app_spec.txt` | Project specification template |
| `security.py` | Bash command security hooks |

## Customization

### Using a Different ClickUp Space

The agent will use `get_workspace_hierarchy` to find available Spaces. You can:
1. Edit `prompts/initializer_prompt.md` to specify a Space name
2. Or let the agent pick the first available Space

### Changing Task Count

Edit `clickup_config.py`:
```python
DEFAULT_TASK_COUNT = 50  # Change this
```

### Custom Status Names

If your ClickUp workspace uses different status names, update `clickup_config.py`:
```python
STATUS_TODO = "to do"        # Change to match your statuses
STATUS_IN_PROGRESS = "in progress"
STATUS_DONE = "complete"
```

## Troubleshooting

### "CLICKUP_API_KEY not set"
Get your API key from https://app.clickup.com/settings/apps

### "CLICKUP_TEAM_ID not set"
Find it in your ClickUp URL: `https://app.clickup.com/[TEAM_ID]/...`

### MCP server not connecting
Ensure Node.js 18+ is installed:
```bash
node --version  # Should be v18 or higher
```

### Tasks not appearing in ClickUp
Check that your API key has permission to create tasks in the target Space.

## Credits

- Original Linear version: [coleam00/Linear-Coding-Agent-Harness](https://github.com/coleam00/Linear-Coding-Agent-Harness)
- Anthropic's autonomous coding quickstart: [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- ClickUp API: [ClickUp API Documentation](https://clickup.com/api)

## License

MIT License - see [LICENSE](LICENSE)
