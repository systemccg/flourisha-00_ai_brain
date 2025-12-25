# Process Idea Workflow

Handle ideas from the Idea Scratchpad list, including YouTube video analysis.

---

## When to Use

- Task appears in Idea Scratchpad list
- Task has `youtube` tag (needs video analysis)
- Task has `needs-research` tag
- User says "process my ideas" or "check the scratchpad"

---

## Workflow Steps

### 1. Fetch Idea Scratchpad Tasks

```python
# List ID: 901112609506
import sys
sys.path.insert(0, "/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference")
from clickup_api import ClickUpClient

client = ClickUpClient()
tasks = client.get_list_tasks("901112609506", statuses=["--", "in progress"])
```

### 2. Triage Each Idea

For each task, determine type:

| Contains | Action |
|----------|--------|
| YouTube URL | Analyze video, extract insights |
| External link | Fetch and summarize content |
| Plain text idea | Assess feasibility, add structure |

### 3. Process YouTube Ideas

When task contains YouTube link:

```markdown
1. Extract video ID from URL
2. Fetch transcript (use youtube-transcript-api or similar)
3. Analyze content for:
   - Core concept/teaching
   - Relevance to Flourisha/PAI
   - Actionable insights
   - Implementation ideas
4. Update task description with:

   ## Video Analysis

   **Title:** {video title}
   **Channel:** {channel name}
   **Why Saved:** {infer from original task context}

   ## Key Insights
   - {insight 1}
   - {insight 2}

   ## Relevance to Flourisha
   {how this applies}

   ## Recommended Action
   - [ ] Graduate to project: {suggested name}
   - [ ] Add to existing project: {project}
   - [ ] Archive (not actionable)
```

### 4. Update Tags

After processing:

| Outcome | Tags to Add | Tags to Remove |
|---------|-------------|----------------|
| Ready for project | `ready-to-graduate` | `needs-research`, `youtube` |
| Needs more work | `needs-research` | - |
| Not actionable | `stale` | `youtube`, `needs-research` |

### 5. Assign Appropriately

- **Flourisha System** - If AI should continue processing
- **Greg Wasmuth** - If needs human decision (status: `in review`)

---

## Example: YouTube Idea Processing

**Original Task:**
```
Name: Check out this AI coding video
Description: https://youtube.com/watch?v=xyz123 - saw on Twitter, looks useful for agents
Tags: youtube, idea
```

**After Processing:**
```
Name: AI Agent Architecture Patterns
Description:
## Video Analysis

**Title:** "Building Production AI Agents - 5 Patterns That Work"
**Channel:** AI Engineering Weekly
**Why Saved:** Relevant to autonomous coding agent development

## Key Insights
- Pattern 1: State machine for agent flow control
- Pattern 2: Tool use with retry logic
- Pattern 3: Human-in-the-loop checkpoints

## Relevance to Flourisha
Direct application to autonomous-coder agent implementation.
Could improve session handoff reliability.

## Recommended Action
- [x] Graduate to project: Autonomous Coder Agent
- [ ] Integrate patterns into existing clickup-tasks skill

Tags: functional, ready-to-graduate
Assignee: Greg Wasmuth (for approval to graduate)
Status: in review
```

---

## Bulk Processing

To process all pending ideas:

```
1. Fetch all tasks from Idea Scratchpad with status "--"
2. Sort by priority (process high priority first)
3. For each task:
   a. Analyze content
   b. Update description
   c. Update tags
   d. Set appropriate assignee
4. Report summary to user
```
