# Feature Implementation Guidelines

**When to create a Skill vs Project**

## TL;DR - Quick Decision Tree

```
New capability requested?
  ├─ Client deliverable with deadline? → PROJECT
  ├─ Major infrastructure overhaul? → PROJECT
  ├─ Research with formal outcome? → PROJECT
  └─ New AI Brain capability? → SKILL ✅
```

---

## The Problem

Previously, every new feature became a standalone project in `01f_Flourisha_Projects/`, creating:
- ❌ Project management overhead for simple features
- ❌ Scattered documentation across many folders
- ❌ Difficulty tracking what's actually a discrete deliverable vs. an integrated capability
- ❌ Cognitive load from tracking too many "projects"

## The Solution: Features as Skills

**PREFERRED APPROACH:** Implement new AI Brain capabilities as **skills**, not projects.

---

## When to Create a SKILL

✅ **Create a skill when adding:**
- New AI Brain capabilities (Gmail integration, Slack integration, etc.)
- API integrations that enhance AI functionality
- Workflow automations
- Data processing pipelines
- Internal tools and utilities
- Anything that extends what Flourisha can do

**Location:** `/root/flourisha/00_AI_Brain/skills/[feature-name]/`

**Structure:**
```
/root/flourisha/00_AI_Brain/skills/gmail-integration/
├── SKILL.md                    # Skill definition with USE WHEN triggers
├── IMPLEMENTATION.md           # Implementation notes (optional)
└── workflows/                  # Workflow scripts (optional)
```

**Documentation:**
- Detailed technical docs go in `/root/flourisha/00_AI_Brain/documentation/services/[feature-name].md`
- Architecture decisions documented in ADRs within the service doc
- Keep SKILL.md concise - link to detailed docs

**Example: Gmail Integration**
- ✅ Skill: `/root/flourisha/00_AI_Brain/skills/gmail-integration/SKILL.md`
- ✅ Docs: `/root/flourisha/00_AI_Brain/documentation/services/gmail-integration.md`
- ❌ Project: ~~`/root/flourisha/01f_Flourisha_Projects/gmail-integration/`~~ (too much overhead!)

---

## When to Create a PROJECT

✅ **Create a project when:**

1. **Client Deliverables**
   - External deadline
   - Contractual obligation
   - Specific client requirements
   - Billable work
   - Example: `benefits-package` (research for IOM)

2. **Major Infrastructure Overhauls**
   - Multi-week effort with phases
   - Cross-system changes
   - Requires formal planning and tracking
   - Example: `flourisha-app` (entire backend system)

3. **Research Initiatives with Formal Outcomes**
   - Defined research questions
   - Deliverable report or presentation
   - Time-boxed investigation
   - Example: `industry-trends-study`

4. **Anything Requiring Dedicated Project Management**
   - Multiple stakeholders
   - Budget tracking
   - Milestone-based delivery
   - External dependencies

**Location:** `/root/flourisha/01f_Flourisha_Projects/[project-name]/`

**Structure:**
```
/root/flourisha/01f_Flourisha_Projects/client-project/
├── README.md
├── SPECS.md
├── ARCHITECTURE.md
├── TESTING.md
├── DEPLOYMENT.md
├── docs/
├── src/ (or link to separate repo)
└── deliverables/
```

**Tracking:** Must be in `PROJECT_REGISTRY.md`

---

## Comparison Table

| Aspect | Skill | Project |
|--------|-------|---------|
| **Purpose** | Extend AI Brain capabilities | Deliver discrete outcome |
| **Tracking** | Skill definition only | Full project management |
| **Documentation** | Concise SKILL.md + detailed service docs | Complete project docs (README, SPECS, etc.) |
| **Location** | `00_AI_Brain/skills/` | `01f_Flourisha_Projects/` |
| **Overhead** | Minimal | Full project lifecycle |
| **Timeline** | Ongoing/integrated | Fixed start/end dates |
| **Examples** | Gmail integration, API wrappers, workflows | Client deliverables, major rewrites |

---

## Migration: Project → Skill

If you realize a "project" is actually a feature:

1. **Move skill definition:**
   ```bash
   mkdir -p /root/flourisha/00_AI_Brain/skills/[feature-name]
   # Create SKILL.md with USE WHEN triggers
   ```

2. **Move documentation:**
   ```bash
   mv project-docs.md /root/flourisha/00_AI_Brain/documentation/services/[feature-name].md
   ```

3. **Remove from PROJECT_REGISTRY:**
   ```bash
   # Delete entry from 01f_Flourisha_Projects/PROJECT_REGISTRY.md
   ```

4. **Delete project folder:**
   ```bash
   rm -rf /root/flourisha/01f_Flourisha_Projects/[feature-name]
   ```

---

## Skill Template

```markdown
---
name: feature-name
description: Brief description. USE WHEN user says "trigger phrase", "other trigger", OR "action keyword". Capabilities summary.
---

# Feature Name Skill

**Status:** Planning | Active | Deprecated
**Priority:** HIGH | MEDIUM | LOW

## Overview
What this skill does and why it exists.

## Workflow Triggers
| User Says | Action |
|-----------|--------|
| "trigger" | What happens |

## Architecture
Key components and data flow.

## Implementation Checklist
- [ ] Phase 1 tasks
- [ ] Phase 2 tasks

## Related Documentation
- Link to detailed docs in `/root/flourisha/00_AI_Brain/documentation/services/`
```

---

## Documentation Strategy

### Skill Documentation (Concise)
**File:** `/root/flourisha/00_AI_Brain/skills/[feature-name]/SKILL.md`
**Content:**
- Skill definition with USE WHEN triggers (REQUIRED for Claude Code)
- High-level overview
- Workflow triggers
- Implementation checklist
- Links to detailed documentation

**Keep it:** 1-2 pages max, scannable

### Service Documentation (Detailed)
**File:** `/root/flourisha/00_AI_Brain/documentation/services/[feature-name].md`
**Content:**
- Full architecture and design
- Architecture Decision Records (ADRs)
- Data flow diagrams
- API specifications
- Database schema
- Security considerations
- Testing strategy
- Implementation timeline

**This is:** The comprehensive reference document

---

## Decision Framework

When a new feature is requested, ask:

### Question 1: Is this a discrete deliverable with external accountability?
- **YES** → Probably a project
- **NO** → Continue to Q2

### Question 2: Does this extend AI Brain capabilities?
- **YES** → Skill ✅
- **NO** → Continue to Q3

### Question 3: Does this require formal project management (milestones, stakeholders, budget)?
- **YES** → Project
- **NO** → Skill ✅

### Question 4: Is this a major multi-week infrastructure overhaul?
- **YES** → Project
- **NO** → Skill ✅

**When in doubt:** Default to **SKILL**. You can always promote to a project later if needed.

---

## Examples

### ✅ Implemented as SKILL

**Gmail Integration**
- Extends AI Brain with email ingestion
- No external deadline
- Integrated capability, not standalone deliverable
- **Location:** `00_AI_Brain/skills/gmail-integration/`

**ClickUp Tasks**
- Workflow automation for task management
- Enhances AI productivity
- Not a discrete project
- **Location:** `00_AI_Brain/skills/clickup-tasks/`

**Fabric Pattern Selection**
- Intelligent CLI wrapper
- No external deliverable
- Internal capability
- **Location:** `00_AI_Brain/skills/fabric/`

### ✅ Implemented as PROJECT

**Flourisha App**
- Major backend application
- Multi-month effort with phases
- Separate codebase and deployment
- Requires formal tracking
- **Location:** `01f_Flourisha_Projects/flourisha-app/`

**Benefits Package Research**
- Client deliverable for IOM
- Specific deadline and scope
- Formal report required
- **Location:** `01f_Flourisha_Projects/benefits-package/`

**Industry Trends Study**
- Research initiative with report
- Time-boxed investigation
- Formal outcome
- **Location:** `01f_Flourisha_Projects/industry-trends-study/`

---

## Benefits of This Approach

### For Skills
- ✅ Minimal overhead
- ✅ Integrated into AI Brain naturally
- ✅ Easy to discover and use (USE WHEN triggers)
- ✅ Documentation co-located with implementation
- ✅ No project management burden

### For Projects
- ✅ Only track what truly needs tracking
- ✅ Clear accountability and deadlines
- ✅ Appropriate level of documentation
- ✅ Formal milestones and deliverables
- ✅ Client-facing or business-critical work

### Overall
- ✅ Reduced cognitive load
- ✅ Clearer separation of concerns
- ✅ Better organization
- ✅ Easier to maintain
- ✅ Scales better as AI Brain grows

---

## Anti-Patterns to Avoid

### ❌ Creating a project for every feature
**Bad:**
```
01f_Flourisha_Projects/
├── gmail-integration/
├── slack-integration/
├── notion-integration/
├── github-integration/
└── ... (50 more "projects")
```

**Good:**
```
00_AI_Brain/skills/
├── gmail-integration/
├── slack-integration/
├── notion-integration/
└── github-integration/
```

---

### ❌ No documentation for skills
**Bad:**
```
skills/gmail-integration/SKILL.md (only)
# No implementation details anywhere
```

**Good:**
```
skills/gmail-integration/SKILL.md (overview + triggers)
documentation/services/gmail-integration.md (full details)
```

---

### ❌ Treating true projects as skills
**Bad:**
```
skills/client-deliverable/ (This is a project!)
```

**Good:**
```
01f_Flourisha_Projects/client-deliverable/
# Full project structure with tracking
```

---

## Summary

**Default to SKILL for new capabilities.**

Only create a PROJECT when:
- External deliverable with deadline
- Major infrastructure overhaul
- Requires formal project management

This keeps the AI Brain clean, maintainable, and focused on integrated capabilities rather than managing dozens of mini-projects.

---

**Created:** 2025-12-13
**Last Updated:** 2025-12-13
**See also:**
- `PROJECT_REGISTRY.md` - What qualifies as a project
- `00_AI_Brain/documentation/README.md` - Documentation structure
- `00_AI_Brain/skills/` - All skills directory
