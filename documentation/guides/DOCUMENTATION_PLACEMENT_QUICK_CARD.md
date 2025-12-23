# Documentation Placement Quick Card

**CRITICAL RULE:** ALL system documentation goes in `/root/flourisha/00_AI_Brain/documentation/` subdirectories, NEVER in the root.

## Quick Decision Tree

### ❓ What are you creating?

**System-level documentation?** 
- ✅ YES → Go to Step 2
- ❌ NO → Create in project directory (e.g., `/root/local-ai-packaged/`)

### ❓ Which category?

| Content | Category Path |
|---------|---------------|
| Phase 2 Docker, setup, status | `documentation/phase2/` |
| Server config, infrastructure, DNS, Traefik | `documentation/infrastructure/` |
| MCP servers, Playwright setup, integrations | `documentation/mcp-servers/` |
| Boot procedures, startup steps | `documentation/startup/` |
| Security policies, firewall, hardening | `documentation/security/` |
| Monitoring, alerts, observability | `documentation/monitoring/` |
| Problem solving, debugging guides | `documentation/troubleshooting/` |
| Old/deprecated documentation | `documentation/archive/` |

### ✅ DO THIS:

```bash
# 1. Create file in correct subdirectory
/root/flourisha/00_AI_Brain/documentation/[CATEGORY]/YOUR_FILE.md

# 2. Update category README.md to add your file
echo "- **[YOUR_FILE.md](./YOUR_FILE.md)** - Brief description" >> \
  /root/flourisha/00_AI_Brain/documentation/[CATEGORY]/README.md

# 3. Update main documentation/README.md if it's a new major section
```

### ❌ DO NOT DO THIS:

```bash
# ❌ WRONG - Creates file in root
/root/flourisha/00_AI_Brain/YOUR_FILE.md

# ❌ WRONG - Creates file outside documentation folder
/root/flourisha/YOUR_FILE.md

# ❌ WRONG - Creates file in projects folder
/root/YOUR_FILE.md
```

## Examples

### WRONG Path ❌
```
/root/flourisha/00_AI_Brain/PHASE2_STATUS.md
/root/flourisha/00_AI_Brain/SERVER_CONFIG.md
/root/flourisha/00_AI_Brain/PLAYWRIGHT_SETUP.md
```

### CORRECT Path ✅
```
/root/flourisha/00_AI_Brain/documentation/phase2/PHASE2_STATUS.md
/root/flourisha/00_AI_Brain/documentation/infrastructure/SERVER_CONFIG.md
/root/flourisha/00_AI_Brain/documentation/mcp-servers/PLAYWRIGHT_SETUP.md
```

## For AI Assistants

Before creating ANY markdown documentation file:

1. ❓ Ask: "Is this system-level documentation?"
   - If NO → Create in project directory
   - If YES → Continue to step 2

2. ❓ Ask: "Which category does it belong to?"
   - Use table above to decide
   - If unsure → Default to `infrastructure/` for general system docs

3. ✅ Create file in: `/root/flourisha/00_AI_Brain/documentation/[CATEGORY]/`

4. ✅ Update: Category README.md with new file entry

5. ✅ Update: Main `documentation/README.md` if needed

6. ✅ Verify: File is NOT in `/root/flourisha/00_AI_Brain/` root

## For Humans (Greg)

If you find documentation in the wrong place:

1. Move it to the correct subdirectory
2. Update all README.md files
3. Remind the AI: "See /root/flourisha/00_AI_Brain/documentation/DOCUMENTATION_GUIDELINES.md"
4. Reference this card

## Full Guidelines

For complete details, see: `/root/flourisha/00_AI_Brain/documentation/DOCUMENTATION_GUIDELINES.md`

---

**Enforced:** 2025-12-05  
**Last Updated:** 2025-12-05
