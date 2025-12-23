# Flourisha Contract

**Version:** 1.0
**Date:** 2025-12-04
**Adapted from:** Daniel Miessler's PAI Contract (2025-11-20)

This document defines what Flourisha (Personal AI Infrastructure) guarantees, what requires configuration, and what is example/community content. This is the **contract** between Flourisha and its user.

---

## What is Flourisha?

**Flourisha is Greg's Personal AI Infrastructure** built on Claude Code.

**Flourisha vs PAI:**
- **PAI** = Daniel Miessler's public template (sanitized framework for everyone)
- **Flourisha** = Greg's private, customized system (personal data, workflows, integrations)

Flourisha was built on PAI's scaffolding but includes personal customizations, contacts, preferences, and integrations specific to Greg's needs.

---

## Core Guarantees (Always Works)

These features work immediately, **requiring no configuration**:

### 1. **Hook System**
- Hooks execute without file-not-found errors
- SessionStart loads CORE context automatically
- Events are captured to history/raw-outputs/
- PAI_DIR defaults to ~/.claude

### 2. **Skills Architecture**
- Skills load and route correctly
- CORE skill provides system context (Flourisha identity, contacts, preferences)
- Skill triggers activate appropriate modules
- Skills symlinked from AI Brain (`/root/flourisha/00_AI_Brain/skills/`)

### 3. **Agents**
- Agent files define specialized personalities
- Task tool launches agents correctly
- Agents available: architect, claude-researcher, designer, engineer, gemini-researcher, pentester, perplexity-researcher, researcher

### 4. **History System (UOCS)**
- Session summaries capture to history/sessions/
- Learnings capture to history/learnings/
- Raw events log to history/raw-outputs/
- Date-based organization (YYYY-MM)

### 5. **Path Resolution**
- Centralized path resolution via `hooks/lib/pai-paths.ts`
- Single source of truth for all directory paths
- Fails fast with clear errors if misconfigured

### 6. **Google Drive Integration**
- Flourisha directory synced to `/root/flourisha/`
- AI Brain at `/root/flourisha/00_AI_Brain/`
- PARA methodology (Projects, Areas, Resources, Archives)
- Bidirectional sync with `flourisha-bisync`

---

## Configured Functionality (Needs Setup)

These features require API keys or external services:

### 1. **Voice Server**
**Requires:**
- `ELEVENLABS_API_KEY` in .env
- `ELEVENLABS_VOICE_ID` in .env
- Voice server running (`bun voice-server/server.ts`)

### 2. **Research Skills**
**Requires:**
- `PERPLEXITY_API_KEY` for perplexity-researcher
- `GOOGLE_API_KEY` for gemini-researcher
- Additional keys for other research agents

### 3. **Fabric Patterns**
**Requires:**
- Fabric CLI installed
- fabric-repo present in skills directory

### 4. **MCP Integrations**
**Requires:**
- API keys for specific providers
- MCP server configuration

---

## Health Check

Run this command to verify Flourisha is working:

```bash
bun ~/.claude/hooks/self-test.ts
```

Expected output:
```
 Flourisha Health Check
============================================================
  PAI_DIR Resolution: PAI_DIR: /root/.claude
  Hooks Directory: Found
  Skills Directory: Found
  Agents Directory: Found
  History Directory: Found
  CORE Skill: Loads correctly
  Settings Configuration: Valid
  Agents: Found 8 agent directories
  Hook Executability: Critical hooks accessible
  PAI Paths Library: Present
  Voice Server: (optional feature)
  Environment Configuration: Present
  Flourisha Directory: Found
  AI Brain Directory: Found
  Skills Symlink: Properly symlinked

 Flourisha is healthy! All core guarantees working.
```

---

## Protection System

### Pre-Commit Validation
Flourisha includes a protection system to prevent accidentally committing sensitive data:

```bash
# Run validation manually
bun ~/.claude/hooks/validate-protected.ts

# Install pre-commit hook
cp ~/.claude/hooks/pre-commit.template .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Protected Patterns
The following patterns are checked:
- API keys (sk-ant-, sk-proj-, ghp_, gho_)
- Passwords and secrets
- Personal email addresses

### Exception Files
Some files are exempt from pattern checking:
- `.env.example`
- `.env.template`
- `.flourisha-protected.json`

---

## What Flourisha Is NOT

Flourisha does NOT guarantee:

1. **Public Compatibility:** This is a private system, not a public template
2. **Portability:** Contains personal data specific to Greg
3. **Support:** Single-user system
4. **Privacy for Others:** Contains Greg's personal information
5. **Production-Ready:** This is personal infrastructure, not a product

---

## Directory Structure

```
~/.claude/                          # PAI_DIR
├── hooks/                          # Event hooks
│   ├── lib/pai-paths.ts           # Centralized path resolution
│   ├── self-test.ts               # Health check system
│   ├── validate-protected.ts      # Security validation
│   ├── pre-commit.template        # Git pre-commit hook
│   ├── capture-all-events.ts      # Event logging
│   ├── load-core-context.ts       # Context injection
│   └── ...
├── skills -> /root/flourisha/00_AI_Brain/skills  # Symlink
├── agents -> /root/flourisha/00_AI_Brain/agents  # Symlink
├── settings.json                   # Claude Code configuration
├── .env                           # API keys (NEVER COMMIT)
├── .flourisha-protected.json      # Protection manifest
└── history/                       # Session history

/root/flourisha/                   # Google Drive sync
├── 00_AI_Brain/                   # AI context and skills
│   ├── skills/                    # Skill definitions
│   ├── agents/                    # Agent definitions
│   └── documentation/             # System documentation
├── 01f_Flourisha_Projects/        # Active projects (PARA)
├── 02f_Flourisha_Areas/           # Ongoing areas (PARA)
├── 03f_Flourisha_Resources/       # Reference materials (PARA)
└── 04f_Flourisha_Archives/        # Archived items (PARA)
```

---

## Quick Commands

```bash
# Health check
bun ~/.claude/hooks/self-test.ts

# Validate before commit
bun ~/.claude/hooks/validate-protected.ts

# Sync Flourisha with Google Drive
flourisha-bisync

# Navigate to Flourisha
flourisha

# Navigate to projects
projects
```

---

## Version History

**v1.0 (2025-12-04):**
- Initial contract adapted from Daniel Miessler's PAI
- Centralized path resolution system
- Self-test health check system
- Protection validation system
- Pre-commit hook template
- Flourisha-specific customizations documented

---

**This is the Flourisha Contract. If core guarantees fail, run self-test.ts to diagnose. If configured features don't work without setup, that's expected.**

 **Flourisha: Greg's Personal AI Infrastructure**
