# META Task Template

The META task serves as the central coordination point for multi-session autonomous coding projects.

---

## Task Name

`[META] Project Progress Tracker`

---

## Task Description Template

```markdown
## Project Overview
[Project name from app_spec.txt]
[1-2 sentence description of what's being built]

## Session Tracking
This task is used for session handoff between coding agents.
Each agent should add a comment summarizing their session before ending.

## Key Milestones
- [ ] Project setup complete (init.sh, git, structure)
- [ ] Core infrastructure working (database, API scaffolding)
- [ ] Primary features implemented (main user flows)
- [ ] All features complete (full functionality)
- [ ] Polish and refinement done (UI, edge cases, testing)

## Project Configuration
- **List ID:** [ClickUp list ID]
- **Total Tasks:** 50
- **Created:** [timestamp]

## Notes
[Any important context about the project, tech stack decisions, or constraints]
```

---

## Session Comment Template

After each coding session, add a comment to the META task:

```markdown
## Session [N] Complete - [Brief Description]

### Completed This Session
- [Task name]: [Brief summary of implementation]
- [Task name]: [Brief summary]

### Current Progress
- Complete: X tasks
- In Progress: Y tasks
- To Do: Z tasks

### Verification Status
- Ran verification tests on: [feature names]
- All previously completed features working: [Yes/No]

### Notes for Next Session
- [Important context or recommendations]
- [Any blockers or concerns]
- [Suggested next task to tackle]

### Git Commits
- [commit hash]: [message]
```

---

## Usage

1. **Create META task** during project initialization
2. **Read META task comments** at start of each coding session
3. **Add session summary comment** before ending each session
4. **Update milestones** as they're completed
