---
name: update-flourisha-brain
description: |
  Updates Flourisha AI Brain documentation after successful sessions or significant changes.

  Analyzes session accomplishments and updates:
  - MASTER_CONTEXT.md with latest commands/procedures
  - Documentation index
  - Relevant category docs (sync, startup, security, etc.)
  - Core skill context if needed

  USE WHEN:
  - User says "update the brain" or "update documentation"
  - After major infrastructure changes
  - After creating new workflows/procedures
  - Session produced valuable new knowledge
  - New commands/aliases created
  - Significant documentation gaps identified

  Can run as:
  - Manual skill invocation (user-triggered)
  - Automatic SessionEnd check (with confirmation)
  - Sub-agent (to save context)

version: 1.0.0
tags: [documentation, maintenance, knowledge-management]
---

# Update Flourisha Brain

**Purpose:** Keep Flourisha AI Brain documentation current with latest procedures, commands, and knowledge.

---

## When to Use This Skill

### Automatic Triggers (with confirmation)
- [ ] Session created new infrastructure (services, scripts, configs)
- [ ] Session fixed critical issues (worth documenting)
- [ ] Session optimized existing systems (new best practices)
- [ ] New commands/aliases added to system
- [ ] Major architectural changes

### Manual Triggers
- User explicitly requests: "update the brain", "document this"
- After testing confirms new procedures work
- When documentation drift noticed (outdated commands)
- After successful troubleshooting (capture solution)

---

## What Gets Updated

### 1. MASTER_CONTEXT.md
**Location:** `/root/flourisha/00_AI_Brain/context/MASTER_CONTEXT.md`

**Update when:**
- New quick commands added
- Sync procedures changed
- Service startup procedures changed
- Key navigation paths changed

**Example updates:**
```markdown
## Google Drive Sync
**Sync Command:**
```bash
flourisha-sync  # Bidirectional sync (updated 2025-11-20)
```
```

### 2. Documentation Categories

**Sync docs:** `/root/flourisha/00_AI_Brain/documentation/sync/`
- Update when sync procedures change
- New safety procedures
- Optimization results

**Startup docs:** `/root/flourisha/00_AI_Brain/documentation/startup/`
- Update when service procedures change
- New services added
- Startup script locations changed

**Security docs:** `/root/flourisha/00_AI_Brain/documentation/security/`
- Update when security procedures added
- New security tools configured
- Vulnerability fixes documented

### 3. Skills Documentation

**When new skills created:**
- Add to skills README
- Update skill registry
- Document skill usage examples

### 4. Core Skill Context

**Location:** `/root/flourisha/00_AI_Brain/skills/CORE/SKILL.md`

**Update rarely, only when:**
- Core preferences change (stack, languages)
- New critical security rules
- Contact information changes
- Response format changes

---

## Update Procedure

### Step 1: Analyze Session

**Questions to answer:**
1. What was accomplished?
2. Were new commands/procedures created?
3. Which documentation categories affected?
4. Is MASTER_CONTEXT outdated?
5. Should this be in quick reference?

**Example analysis:**
```
Session accomplished:
- Fixed Google Drive sync (deleted folders issue)
- Changed from push/pull to bisync
- Created new flourisha-sync command
- Moved docs to proper location

Affected documentation:
- MASTER_CONTEXT.md (sync commands outdated)
- documentation/sync/*.md (all updated)
- QUICK_REFERENCE.md (maybe add flourisha-sync)

Action: Update MASTER_CONTEXT.md sync section
```

### Step 2: Identify Outdated Content

**Common drift patterns:**
- Old commands that no longer exist
- Procedures that changed
- Paths that moved
- New best practices not documented

**Check these files:**
```bash
# Quick scan for outdated references
grep -r "flourisha-push\|flourisha-pull" /root/flourisha/00_AI_Brain/context/
grep -r "old-command" /root/flourisha/00_AI_Brain/documentation/
```

### Step 3: Update Files

**Priority order:**
1. **MASTER_CONTEXT.md** - Quick reference (most important)
2. **Specific category docs** - Detailed guides
3. **Documentation index** - Discovery
4. **QUICK_REFERENCE.md** - If one-liners added
5. **CORE/SKILL.md** - Only if core changes

**Update template:**
```markdown
<!-- Update timestamp -->
**Last Updated:** 2025-11-20

<!-- Update version if major change -->
**Version:** 1.1

<!-- Add what changed in comment -->
<!-- Updated sync commands from push/pull to bisync -->
```

### Step 4: Sync to Google Drive

**After updates:**
```bash
# Sync updated docs to Google Drive
flourisha-sync

# Verify sync
tail /var/log/pai_flourisha_bisync.log
```

### Step 5: Verify Updates

**Checklist:**
- [ ] MASTER_CONTEXT.md updated with new commands/procedures
- [ ] Relevant category docs updated
- [ ] Documentation index reflects changes
- [ ] No broken links in updated docs
- [ ] Synced to Google Drive
- [ ] Timestamp updated

---

## Implementation Approaches

### Approach 1: Manual Skill (Simplest)

**When user says:** "Update the brain" or "Document this"

**Action:**
1. Ask what changed/was accomplished
2. Identify affected documentation
3. Update relevant files
4. Sync to Google Drive
5. Confirm completion

**Usage:**
```
User: "We just fixed the sync system, update the brain"
Flourisha: *Analyzes session*
Flourisha: I'll update:
- MASTER_CONTEXT.md (sync commands)
- documentation/sync/* (procedures)

*Makes updates*

Flourisha: Updated and synced to Google Drive ✓
```

### Approach 2: Sub-Agent (Context-Efficient)

**Use Task tool to spawn documentation update agent:**

```typescript
// In session
if (majorChanges) {
  Task({
    subagent_type: "architect", // Or create "documentation-updater"
    prompt: `Update Flourisha brain documentation based on:

    Session accomplishments:
    - ${accomplishments}

    Files changed:
    - ${filesChanged}

    Update MASTER_CONTEXT.md and relevant docs in:
    /root/flourisha/00_AI_Brain/

    Then sync to Google Drive with: flourisha-sync`
  });
}
```

### Approach 3: SessionEnd Hook (Automatic with confirmation)

**Add to SessionEnd hook:**

**File:** `/root/.claude/hooks/session-end-doc-check.ts`

```typescript
// After session summary captured
const significantChanges = analyzeChanges(sessionSummary);

if (significantChanges.needsDocUpdate) {
  console.log(`<user-prompt>
Session created significant changes:
${significantChanges.summary}

Would you like to update Flourisha brain documentation?
[Yes] [No] [What would be updated?]
</user-prompt>`);
}
```

---

## Recommended: Hybrid Approach

**Combine all three:**

1. **Manual trigger** - User says "update the brain"
   - Flourisha analyzes session
   - Updates docs
   - Syncs

2. **Automatic check** - SessionEnd hook
   - IF significant infrastructure changes
   - THEN offer to update docs
   - User confirms or declines

3. **Sub-agent for large updates** - Complex sessions
   - Spawn documentation-updater agent
   - Agent analyzes all changes
   - Updates multiple doc categories
   - Syncs to Google Drive
   - Returns summary

---

## Examples

### Example 1: Sync System Change

**Session:** Fixed Google Drive sync, changed to bisync

**Updates needed:**
```bash
# MASTER_CONTEXT.md
OLD:
```bash
flourisha-pull  # Pull from Google Drive
flourisha-push  # Push to Google Drive
```

NEW:
```bash
flourisha-sync  # Bidirectional sync
```

# documentation/sync/SYNC_GUIDE.md
- Already updated during session ✓

# QUICK_REFERENCE.md
Add:
```bash
flourisha-sync    # Sync Google Drive bidirectionally
```
```

**Command:**
```
User: "Update the brain with the new sync commands"
Flourisha: *Updates MASTER_CONTEXT.md*
Flourisha: *Updates QUICK_REFERENCE.md*
Flourisha: *Syncs to Google Drive*
Flourisha: "Brain updated with flourisha-sync command ✓"
```

### Example 2: New Service Added

**Session:** Installed and configured Uptime Kuma

**Updates needed:**
- MASTER_CONTEXT.md (add to Key Services)
- documentation/monitoring/uptime-kuma.md (create)
- documentation/startup/services.md (add startup)

**Command:**
```
User: "Document the Uptime Kuma setup"
Flourisha: *Spawns documentation-updater sub-agent*
Agent: *Creates uptime-kuma.md*
Agent: *Updates MASTER_CONTEXT.md*
Agent: *Updates startup docs*
Agent: *Syncs to Google Drive*
Flourisha: "Uptime Kuma documented in monitoring/ ✓"
```

### Example 3: Security Procedure

**Session:** Configured Cloudflare firewall rules

**Updates needed:**
- documentation/security/firewall.md (update)
- MASTER_CONTEXT.md (maybe quick check command)

**Command:**
```
SessionEnd: "Session created firewall rules - update docs? [Yes/No]"
User: Yes
Flourisha: *Updates security/firewall.md*
Flourisha: *Syncs to Google Drive*
```

---

## Configuration

### Enable Auto-Check at SessionEnd

**File:** `/root/.claude/settings.json`

Add to SessionEnd hooks:
```json
{
  "type": "command",
  "command": "${PAI_DIR}/hooks/check-doc-updates.ts"
}
```

### Manual Invocation

Just activate this skill:
```
User: "update-flourisha-brain" or "update the brain"
```

---

## Success Criteria

**Documentation is current when:**
- [ ] MASTER_CONTEXT.md has latest commands
- [ ] No references to deleted commands
- [ ] New procedures documented in correct category
- [ ] Documentation index reflects structure
- [ ] All docs synced to Google Drive
- [ ] Timestamps updated
- [ ] Links not broken

---

## Maintenance

### Weekly Check
```bash
# Search for common outdated patterns
cd /root/flourisha/00_AI_Brain

# Old sync commands
grep -r "flourisha-push\|flourisha-pull" context/ documentation/

# Outdated paths
grep -r "/root/pai" context/ documentation/

# Missing docs
ls documentation/ | while read dir; do
  [ ! -f "documentation/$dir/README.md" ] && echo "Missing: $dir/README.md"
done
```

### After Major Changes

**Always update brain after:**
- Infrastructure changes
- New services deployed
- Command/alias changes
- Workflow improvements
- Issue resolutions worth documenting

---

## Related Skills

- **CORE** - Core context loaded every session
- **create-skill** - Creating new skills
- **prompting** - Documentation best practices

---

**Last Updated:** 2025-11-20
**Version:** 1.0.0
**Maintainer:** Flourisha AI Brain
