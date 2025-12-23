---
name: daily-roadmap
description: AI-powered morning planning that synthesizes session history and projects into a 2-minute daily roadmap. USE WHEN user says 'daily roadmap', 'start my day', 'morning planning', 'what should I focus on today', or begins a new work session.
---

# Daily Roadmap

AI-powered morning planning that generates a prioritized daily plan in under 2 minutes.

## When to Activate

- Start of work day
- User asks for daily planning
- User needs refocus during day
- Beginning of new session

## Core Workflow

### Step 1: Gather Context (30 seconds)

1. **Read Recent Sessions**: Get last 3 session logs from `${PAI_DIR}/history/sessions/YYYY-MM/`
   ```bash
   ls -t ${PAI_DIR}/history/sessions/$(date +%Y-%m)/*.md | head -3
   ```

2. **Check Active Projects**: Read `PROJECT_REGISTRY.md` for project status
   ```bash
   cat /root/flourisha/01f_Flourisha_Projects/PROJECT_REGISTRY.md
   ```

3. **Note Incomplete Work**: Identify any in-progress items from yesterday

### Step 2: Analyze & Prioritize (30 seconds)

1. Identify incomplete work that needs continuation
2. Apply brutal prioritization framework:
   - **Must**: Will cause problems if not done today
   - **Should**: Important but can wait if needed
   - **Could**: Nice-to-have, can defer
3. Determine **THE ONE THING** for today
4. Create tiered task list

### Step 3: Generate Output (30 seconds)

Use this exact template:

```markdown
# Daily Roadmap - YYYY-MM-DD

## 🎯 THE ONE THING
[Single most critical task for today - if only one thing gets done, this is it]

## ⚡ CRITICAL PATH
[2-3 must-complete items that block other work]

## 📋 TIERED PRIORITIES

### Tier 1: Must Complete
- [ ] [Task that will cause problems if not done]
- [ ] [Second critical task]

### Tier 2: If Time Permits
- [ ] [Important but deferrable]
- [ ] [Would be nice to finish]

### Tier 3: Can Defer
- [ ] [Low priority item]
- [ ] [Backlog item]

## 🔗 CONTINUITY
[What was in progress yesterday that needs completion]
[Context from recent sessions to maintain momentum]

## 🎲 EXECUTION STRATEGY
[How to approach the day - when to do deep work, meetings, breaks]
[Recommended order of tasks]

## ✅ SUCCESS CRITERIA
[What "done" looks like at end of day]
[Measurable outcomes]
```

### Step 4: Save & Display

1. Save roadmap to: `${PAI_DIR}/history/roadmaps/YYYY-MM-DD.md`
2. Display formatted roadmap to user

## Key Principles

1. **2-Minute Rule**: Total execution must be under 2 minutes
2. **ONE Thing Focus**: Always identify single most important task
3. **Continuity**: Never lose context from previous sessions
4. **Strategic Alignment**: All priorities should serve main goals
5. **Brutal Honesty**: Call out misalignment or drift when detected

## Refocus Mode

When user says "refocus" or "what should I work on?" mid-day:

1. Check if today's roadmap exists: `${PAI_DIR}/history/roadmaps/$(date +%Y-%m-%d).md`
2. If exists: Load and show current Tier 1 status
3. Recommend next action based on time remaining
4. If not exists: Generate fresh roadmap

## Examples

**Example 1: Morning Start**
```
User: "start my day"
→ Reads last 3 sessions from history/sessions/2025-12/
→ Checks PROJECT_REGISTRY.md for active work
→ Identifies THE ONE THING: "Complete daily-roadmap skill implementation"
→ Creates tiered priorities based on session context
→ Saves to history/roadmaps/2025-12-05.md
→ Displays formatted roadmap
```

**Example 2: Mid-Day Refocus**
```
User: "what should I work on?"
→ Loads today's roadmap from history/roadmaps/2025-12-05.md
→ Shows Tier 1 progress (1/3 complete)
→ Recommends: "Focus on task 2: Write PROJECT_REGISTRY"
```

**Example 3: No Previous Context**
```
User: "daily roadmap" (first day or no sessions)
→ Notes: No recent session history found
→ Asks user for today's priorities
→ Generates roadmap from user input
→ Saves and displays
```

## Integration Points

- **Session History**: `${PAI_DIR}/history/sessions/YYYY-MM/`
- **Project Registry**: `/root/flourisha/01f_Flourisha_Projects/PROJECT_REGISTRY.md`
- **Saved Roadmaps**: `${PAI_DIR}/history/roadmaps/`
- **CORE Skill**: Inherits global context and principles

## Error Handling

- If no sessions found: Ask user for context
- If PROJECT_REGISTRY missing: Create minimal version
- If roadmaps directory missing: Create it
- Always produce output even with minimal context
