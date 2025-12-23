# Flourisha Documentation Guidelines

**CRITICAL RULE (Non-Negotiable):**
> **ALL system-level documentation MUST go in `/root/flourisha/00_AI_Brain/documentation/`**
> 
> **NEVER create markdown files in:**
> - `/root/` (root directory)
> - `/root/flourisha/` (Flourisha root)
> - `/root/flourisha/00_AI_Brain/` (AI Brain root - only README.md and QUICK_REFERENCE.md allowed)

## Why This Rule Exists

1. **Single Source of Truth** - All system docs in one organized location
2. **Google Drive Sync** - Documentation syncs with Obsidian when organized properly
3. **Discoverability** - Clear categories make finding information easy
4. **Scalability** - System grows without becoming a mess
5. **Maintainability** - Future modifications stay organized

## Documentation Organization

```
/root/flourisha/00_AI_Brain/
├── README.md                              ✅ ALLOWED
├── QUICK_REFERENCE.md                     ✅ ALLOWED
│
└── documentation/                         ← ALL OTHER DOCS HERE
    ├── README.md                          (Index of all documentation)
    ├── DOCUMENTATION_GUIDELINES.md        (This file - enforcement rules)
    │
    ├── phase2/                            (Phase 2 Docker Migration docs)
    │   ├── README.md                      (Phase 2 index)
    │   ├── PHASE2_STATUS.md
    │   ├── PHASE2_QUICK_START.md
    │   ├── PHASE2_DOCKER_MIGRATION_PLAN.md
    │   └── AGENT_SANDBOX_QUICK_START.md
    │
    ├── infrastructure/                    (Server & infrastructure setup)
    │   ├── README.md                      (Infrastructure index)
    │   ├── SERVER_CONFIG.md
    │   ├── DNS_CONFIGURATION_FIX.md
    │   ├── TRAEFIK_SETUP.md
    │   └── DOCKER_DAEMON_CONFIG.md
    │
    ├── mcp-servers/                       (MCP server documentation)
    │   ├── README.md                      (MCP servers index)
    │   ├── PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md
    │   ├── AGENT_SANDBOX_MCP.md
    │   └── MCP_SERVER_SETUP.md
    │
    ├── startup/                           (System startup & boot procedures)
    │   ├── README.md                      (Startup procedures index)
    │   └── STARTUP_CHECKLIST.md
    │
    ├── security/                          (Security configurations & protocols)
    │   ├── README.md                      (Security docs index)
    │   └── SECURITY_CHECKLIST.md
    │
    ├── monitoring/                        (Monitoring & observability)
    │   ├── README.md                      (Monitoring index)
    │   └── MONITORING_SETUP.md
    │
    ├── troubleshooting/                   (Problem resolution & debugging)
    │   ├── README.md                      (Troubleshooting index)
    │   └── [specific issue docs]
    │
    └── archive/                           (Historical & deprecated docs)
        └── [archived documentation]
```

## Decision Tree for File Placement

**Before creating ANY new documentation file, answer these questions:**

### Q1: Is this system-level documentation?
- **YES** → Continue to Q2
- **NO** → Create in project directory (e.g., `/root/local-ai-packaged/`, `/root/wordpress-backup/`)

### Q2: Which category does it belong to?

| Content | Category | Example |
|---------|----------|---------|
| Phase 2 Docker migration, setup, status | `documentation/phase2/` | PHASE2_STATUS.md, PHASE2_QUICK_START.md |
| Server config, infrastructure, DNS, Traefik | `documentation/infrastructure/` | SERVER_CONFIG.md, DNS_CONFIGURATION_FIX.md |
| MCP servers, integrations, Playwright setup | `documentation/mcp-servers/` | PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md |
| Boot procedures, startup steps | `documentation/startup/` | STARTUP_CHECKLIST.md |
| Security policies, firewall rules | `documentation/security/` | SECURITY_CHECKLIST.md |
| Monitoring, alerts, observability | `documentation/monitoring/` | MONITORING_SETUP.md |
| Problem solving, debugging guides | `documentation/troubleshooting/` | [Issue-specific docs] |
| Old/deprecated documentation | `documentation/archive/` | Previously useful but no longer current |

### Q3: Create or Update?

**If file exists:** Use `Edit` tool to update it
**If file is new:** 
1. Verify the correct category from Q2
2. Use `bash cat >` command to create file (avoids Write tool limitation)
3. Update the category README.md to index the new file
4. Update main documentation/README.md

## Enforcement Mechanisms

### For AI Assistants (You)

**BEFORE creating any markdown file:**
1. ❓ Ask yourself: "Where does this file belong?"
2. ✅ Check if it fits one of the categories above
3. ✅ If creating in documentation/, use category subdirectory
4. ✅ If creating in AI Brain root, STOP and reconsider
5. ✅ After creation, update the appropriate README.md

**MANDATORY CHECKS:**
- [ ] File is in correct subdirectory (not in root)
- [ ] File name is descriptive and matches convention
- [ ] Category README.md has been updated with new file
- [ ] Main documentation/README.md is current
- [ ] No TODO or FIXME comments left in final file

### For Humans (Greg)

**If you see documentation in the wrong place:**
1. Move it to correct subdirectory
2. Update all README.md files
3. Run `flourisha-bisync` to sync changes
4. Remind the AI assistant of these guidelines

## Correct vs Incorrect Paths

### ❌ WRONG PATHS (Do NOT create here):

```bash
/root/flourisha/00_AI_Brain/PHASE2_STATUS.md              ❌ ROOT
/root/flourisha/00_AI_Brain/SERVER_CONFIG.md             ❌ ROOT
/root/flourisha/00_AI_Brain/DOCUMENTATION_GUIDELINES.md  ❌ ROOT (except if needed for redirect)
```

### ✅ CORRECT PATHS:

```bash
/root/flourisha/00_AI_Brain/documentation/phase2/PHASE2_STATUS.md              ✅ CORRECT
/root/flourisha/00_AI_Brain/documentation/infrastructure/SERVER_CONFIG.md      ✅ CORRECT
/root/flourisha/00_AI_Brain/documentation/DOCUMENTATION_GUIDELINES.md          ✅ CORRECT
```

## File Naming Conventions

**Use UPPER_CASE_WITH_UNDERSCORES for markdown files:**
- ✅ `PHASE2_STATUS.md`
- ✅ `SERVER_CONFIG.md`
- ✅ `DNS_CONFIGURATION_FIX.md`
- ❌ `phase2-status.md` (use underscores, not hyphens)
- ❌ `Phase2Status.md` (use UPPER_CASE, not camelCase)

**Each category folder should have a README.md index:**
- `/root/flourisha/00_AI_Brain/documentation/phase2/README.md`
- `/root/flourisha/00_AI_Brain/documentation/infrastructure/README.md`
- etc.

## README.md Index Template

Each category should have a README.md that indexes its contents:

```markdown
# [Category Name]

[Brief description of what this category contains]

## Files in This Category

- **[FILENAME.md](./FILENAME.md)** - Brief description
- **[ANOTHER_FILE.md](./ANOTHER_FILE.md)** - Brief description

## Related Categories

- [Other Category](../other-category/)

## Quick Start

[Optional: Quick start steps if applicable]
```

## Google Drive Sync

**After creating/moving documentation:**

```bash
# Sync changes to Google Drive
flourisha-bisync
```

This ensures:
- Documentation syncs to the shared Flourisha_gDrive
- Updates appear in Obsidian (Windows: G:\Shared drives\Flourisha_gDrive)
- Single source of truth maintained

## Troubleshooting Documentation Organization

### Q: What if I'm not sure which category a doc belongs in?

**A:** Choose the closest match, then ask yourself:
- Is it about **building/deploying Phase 2**? → `phase2/`
- Is it about **server/infrastructure setup**? → `infrastructure/`
- Is it about **MCP integration**? → `mcp-servers/`
- Is it about **system startup**? → `startup/`
- Is it about **security**? → `security/`
- Is it about **monitoring/alerts**? → `monitoring/`
- Is it about **fixing a problem**? → `troubleshooting/`
- Is it **outdated/deprecated**? → `archive/`

If still unsure, default to **infrastructure/** for general system docs.

### Q: Can I create new categories?

**A:** Only if necessary. Before creating a new category:
1. Check if existing categories work
2. Plan to have 3+ documents in the category
3. Update this guidelines file to document the new category
4. Create README.md for the new category
5. Update main documentation/README.md

### Q: What about project-specific documentation?

**A:** Keep project docs IN the project directory:
- `/root/local-ai-packaged/` → Local AI project docs
- `/root/wordpress-backup/` → WordPress backup docs
- `/root/traefik/` → Traefik config docs

Only SYSTEM-LEVEL documentation (shared across multiple projects) goes in `/root/flourisha/00_AI_Brain/documentation/`.

## Enforcement History

**Files Moved to Correct Locations (2025-12-05):**

| Original Location | New Location | Category |
|-------------------|--------------|----------|
| `/root/flourisha/00_AI_Brain/PHASE2_STATUS.md` | `/root/flourisha/00_AI_Brain/documentation/phase2/PHASE2_STATUS.md` | phase2 |
| `/root/flourisha/00_AI_Brain/PHASE2_QUICK_START.md` | `/root/flourisha/00_AI_Brain/documentation/phase2/PHASE2_QUICK_START.md` | phase2 |
| `/root/flourisha/00_AI_Brain/SERVER_CONFIG.md` | `/root/flourisha/00_AI_Brain/documentation/infrastructure/SERVER_CONFIG.md` | infrastructure |
| `/root/flourisha/00_AI_Brain/DNS_CONFIGURATION_FIX.md` | `/root/flourisha/00_AI_Brain/documentation/infrastructure/DNS_CONFIGURATION_FIX.md` | infrastructure |
| `/root/flourisha/00_AI_Brain/PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md` | `/root/flourisha/00_AI_Brain/documentation/mcp-servers/PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md` | mcp-servers |
| `/root/flourisha/00_AI_Brain/AGENT_SANDBOX_QUICK_START.md` | `/root/flourisha/00_AI_Brain/documentation/phase2/AGENT_SANDBOX_QUICK_START.md` | phase2 |

---

**Last Updated:** 2025-12-05
**Version:** 1.0
**Enforced By:** Claude Code + PAI System

This guideline is NON-NEGOTIABLE. All system documentation must follow this structure.
