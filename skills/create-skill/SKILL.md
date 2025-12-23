---
name: create-skill
description: |
  Guide for creating new skills in Flourisha's AI Brain following modern best practices.

  Creates skills with:
  - A2A protocol integration (skill-card.json)
  - Proper documentation placement
  - Skills registry updates
  - Google Drive sync

  USE WHEN user wants to create, update, or structure a new skill that extends capabilities
  with specialized knowledge, workflows, or tool integrations.

  Follows Anthropic skill standards + PAI patterns + A2A protocol.
version: 2.0.0
---

# Create Skill - Skill Creation Framework

## When to Activate This Skill
- "Create a new skill for X"
- "Build a skill that does Y"
- "Add a skill for Z"
- "Update/improve existing skill"
- "Structure a skill properly"
- User wants to extend Kai's capabilities

## Core Skill Creation Workflow

### Step 1: Understand the Purpose
Ask these questions:
- **What does this skill do?** (Clear, specific purpose)
- **When should it activate?** (Trigger conditions)
- **What tools/commands does it use?** (Dependencies)
- **Is it simple or complex?** (Determines structure)

### Step 2: Choose Skill Type

**Simple Skill** (SKILL.md only):
- Single focused capability
- Minimal dependencies
- Quick reference suffices
- Examples: fabric-patterns, youtube-extraction

**Complex Skill** (SKILL.md + CLAUDE.md + supporting files):
- Multi-step workflows
- Extensive context needed
- Multiple sub-components
- Examples: development, website, consulting

### Step 3: Create Directory Structure

**Location:** `/root/flourisha/00_AI_Brain/skills/[skill-name]/`
(Symlinked to `~/.claude/skills/` for Claude Code compatibility)

```bash
# Simple skill
/root/flourisha/00_AI_Brain/skills/[skill-name]/
├── SKILL.md          # Required
└── skill-card.json   # Required (A2A protocol)

# Complex skill
/root/flourisha/00_AI_Brain/skills/[skill-name]/
├── SKILL.md           # Quick reference
├── CLAUDE.md          # Full context
├── skill-card.json    # A2A metadata
├── workflows/         # Workflow docs (optional)
├── examples/          # Usage examples (optional)
└── assets/           # Supporting files (optional)
```

**IMPORTANT:** Skills go in `/root/flourisha/00_AI_Brain/skills/`, NOT `~/.claude/skills/`
(The latter is a symlink for vendor compatibility)

### Step 4: Write SKILL.md (Required)

Use this structure:
```markdown
---
name: skill-name
description: Clear description of what skill does and when to use it. Should match activation triggers.
---

# Skill Name

## When to Activate This Skill
- Trigger condition 1
- Trigger condition 2
- User phrase examples

## [Main Content Sections]
- Core workflow
- Key commands
- Examples
- Best practices

## Supplementary Resources
For detailed context: `read ${PAI_DIR}/skills/[skill-name]/CLAUDE.md`
```

### Step 5: Write CLAUDE.md (If Complex)

Include:
- Comprehensive methodology
- Detailed workflows
- Component documentation
- Advanced usage patterns
- Integration instructions
- Troubleshooting guides

### Step 6: Create skill-card.json (A2A Protocol)

**Location:** `/root/flourisha/00_AI_Brain/skills/[skill-name]/skill-card.json`

```json
{
  "name": "skill-name",
  "description": "Same as SKILL.md frontmatter description",
  "version": "1.0.0",
  "triggers": [
    "user phrase 1",
    "user phrase 2",
    "activation trigger 3"
  ],
  "capabilities": [
    "capability-1",
    "capability-2"
  ],
  "requires": {
    "tools": ["tool1", "tool2"],
    "mcpServers": ["server1"],
    "skills": ["other-skill"]
  }
}
```

**Why:** A2A protocol enables skill discovery and interoperability

### Step 7: Update Skills Registry

**Location:** `/root/flourisha/00_AI_Brain/a2a/registry/skills.json`

Add entry:
```json
{
  "id": "skill-name",
  "name": "Skill Name",
  "description": "Brief description",
  "category": "documentation|automation|development|research|security|monitoring",
  "version": "1.0.0",
  "location": "/root/flourisha/00_AI_Brain/skills/skill-name",
  "tags": ["tag1", "tag2"]
}
```

**Categories:**
- `documentation` - Doc creation/management
- `automation` - Workflow automation
- `development` - Code development
- `research` - Information gathering
- `security` - Security tasks
- `monitoring` - System monitoring
- `knowledge-management` - Knowledge capture
- `infrastructure` - System infrastructure

### Step 8: Check Documentation Placement

**IF skill creates documentation:**

Ask: Is this system-level or project-specific?

**System-level docs** → `/root/flourisha/00_AI_Brain/documentation/[category]/`
- Sync procedures
- Security guides
- Monitoring docs
- Infrastructure specs

**Project-specific docs** → Stay in project directory
- `/root/local-ai-packaged/CONTEXT.md`
- `/root/mcp/n8n-mcp/README.md`

**Skill documentation** → Stay in skill directory
- Skill workflows
- Skill examples
- Skill methodology

**See:** `/root/flourisha/00_AI_Brain/documentation/DOCUMENTATION_GUIDELINES.md`

### Step 9: Sync to Google Drive

After creating skill:
```bash
flourisha-sync
```

This makes skill available:
- On server: `/root/flourisha/00_AI_Brain/skills/`
- On Google Drive: `Flourisha_gDrive/00_AI_Brain/skills/`
- In Obsidian: `G:\Shared drives\Flourisha_gDrive\00_AI_Brain\skills/`

### Step 10: Test the Skill

1. Trigger it with natural language
2. Verify it loads correctly
3. Check all references work
4. Validate against examples

## Skill Naming Conventions

- **Lowercase with hyphens**: `create-skill`, `web-scraping`
- **Descriptive, not generic**: `fabric-patterns` not `text-processing`
- **Action or domain focused**: `ai-image-generation`, `chrome-devtools`

## Description Best Practices

Your description should:
- Clearly state what the skill does
- Include trigger phrases (e.g., "USE WHEN user says...")
- Mention key tools/methods used
- Be concise but complete (1-3 sentences)

**Good examples:**
- "Multi-source comprehensive research using perplexity-researcher, claude-researcher, and gemini-researcher agents. Launches up to 10 parallel research agents for fast results. USE WHEN user says 'do research', 'research X', 'find information about'..."
- "Chrome DevTools MCP for web application debugging, visual testing, and browser automation. The ONLY acceptable way to debug web apps - NEVER use curl, fetch, or wget."

## Templates Available

- `simple-skill-template.md` - For straightforward capabilities
- `complex-skill-template.md` - For multi-component skills
- `skill-with-agents-template.md` - For skills using sub-agents

## Supplementary Resources

For complete guide with examples: `read ${PAI_DIR}/skills/create-skill/CLAUDE.md`
For templates: `ls ${PAI_DIR}/skills/create-skill/templates/`

## Modern Skill Requirements (2025)

**Every skill MUST have:**
1. ✅ SKILL.md with YAML frontmatter
2. ✅ skill-card.json (A2A protocol)
3. ✅ Entry in skills registry
4. ✅ Synced to Google Drive

**Best practices:**
5. ✅ Progressive disclosure (SKILL.md → CLAUDE.md → components)
6. ✅ Clear activation triggers in description
7. ✅ Imperative/infinitive instructions (verb-first)
8. ✅ No duplication of global context
9. ✅ Proper documentation placement
10. ✅ Version controlled and tested

## Key Principles

1. **Progressive disclosure**: SKILL.md = quick reference, CLAUDE.md = deep dive
2. **Clear activation triggers**: User should know when skill applies
3. **Executable instructions**: Imperative/infinitive form (verb-first)
4. **Context inheritance**: Skills inherit global context automatically
5. **No duplication**: Reference global context, don't duplicate it
6. **Self-contained**: Skill should work independently
7. **Discoverable**: Description + skill-card.json enable intent matching
8. **A2A compliant**: skill-card.json for interoperability
9. **Properly placed**: Skills in AI Brain, docs in documentation/
10. **Synced**: Available across server, Google Drive, and Obsidian
