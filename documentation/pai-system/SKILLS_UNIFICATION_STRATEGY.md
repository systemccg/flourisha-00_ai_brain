# Skills Unification Strategy

**Date:** 2025-12-04
**Version:** 1.0
**Purpose:** Single source of truth for all skills across PAI ecosystem

---

## Problem Statement

Skills were historically created in multiple locations:
- ❌ Some in `/root/.claude/skills/` (suboptimal)
- ✅ Some in `/root/flourisha/00_AI_Brain/skills/` (correct location)

This creates confusion about where to work and risks divergence.

---

## Current State

### ✅ What's Working

1. **Symlink in Place**
   - `/root/.claude/skills/` → `/root/flourisha/00_AI_Brain/skills/` (working symlink)
   - Claude Code reads through symlink correctly
   - No actual duplication

2. **No Divergence Detected**
   - All 16 skills are unified
   - No conflicting versions between locations

### ⚠️ The Risk

1. **Future Confusion**
   - New developers might not know symlink exists
   - They might create skills in `/root/.claude/skills/` thinking it's the source
   - Over time this could diverge and create maintenance headaches

2. **Organizational Clarity**
   - Users see both paths as valid
   - No enforcement prevents ad-hoc placement
   - Documentation unclear about single source of truth

---

## Solution: Three-Layer Enforcement

### Layer 1: Documentation (You are here) 📚

**Golden Rule:**
> **ALL skills live in `/root/flourisha/00_AI_Brain/skills/`**
>
> `/root/.claude/skills/` is a symlink for convenience only.
>
> Never create anything directly in `.claude/skills/`

### Layer 2: Pre-Commit Hook (Automated Prevention) 🛡️

Create a Git pre-commit hook that validates:
- ❌ Prevent commits that add files to `/root/.claude/skills/`
- ❌ Warn if SKILL.md exists in both locations (divergence detected)
- ✅ Allow commits to `/root/flourisha/00_AI_Brain/skills/`

**Hook File:** `/root/flourisha/00_AI_Brain/hooks/skills-unification-check.sh`

```bash
#!/bin/bash
set -e

CLAUDE_SKILLS="/root/.claude/skills"
FLOURISHA_SKILLS="/root/flourisha/00_AI_Brain/skills"

# Check for new files in .claude/skills that aren't symlinks
if git diff --cached --name-only | grep -q "^\.claude/skills/"; then
  echo "❌ ERROR: Attempted to commit files to /root/.claude/skills/"
  echo "💡 SOLUTION: All skills must go in /root/flourisha/00_AI_Brain/skills/"
  echo "             /root/.claude/skills/ is a symlink and read-only."
  exit 1
fi

# Check for skill divergence (same skill in both locations with different content)
for skill_dir in "$FLOURISHA_SKILLS"/*; do
  skill_name=$(basename "$skill_dir")
  if [ -d "$CLAUDE_SKILLS/$skill_name" ] && [ ! -L "$CLAUDE_SKILLS/$skill_name" ]; then
    if ! diff -r "$CLAUDE_SKILLS/$skill_name" "$skill_dir" >/dev/null 2>&1; then
      echo "⚠️  WARNING: Skill '$skill_name' has diverged between locations"
      echo "   Run: cp -r $skill_dir $CLAUDE_SKILLS/$skill_name"
    fi
  fi
done

echo "✅ Skills unification check passed"
```

### Layer 3: File System Protections (Read-Only) 🔒

Make the `.claude/skills/` directory read-only to prevent accidental direct edits:

```bash
# Make symlink target obvious (make .claude/skills harder to treat as primary)
chmod 555 /root/.claude/skills  # Read-only, prevents new files

# If someone tries to create a skill there, they get an error:
# -bash: cannot create /root/.claude/skills/new-skill: Permission denied
```

---

## Developer Workflow

### ✅ Correct Way

```bash
# 1. All skill work happens here:
cd /root/flourisha/00_AI_Brain/skills/my-new-skill

# 2. Create SKILL.md in this directory
nano SKILL.md

# 3. Commit to Git
git add my-new-skill/
git commit -m "Add my-new-skill"

# 4. Sync to Google Drive (if in Flourisha drive)
flourisha-sync
```

### ❌ Don't Do This

```bash
# ❌ WRONG: Working in .claude/skills
cd /root/.claude/skills/my-new-skill

# ❌ WRONG: Creating files here
nano /root/.claude/skills/my-new-skill/SKILL.md
```

### If You Accidentally Create in `.claude/skills/`

```bash
# 1. Copy to correct location
cp -r /root/.claude/skills/my-skill /root/flourisha/00_AI_Brain/skills/

# 2. Delete from wrong location (symlink will still work)
rm -rf /root/.claude/skills/my-skill  # This just removes from Flourisha too via symlink

# 3. Recreate properly
mkdir /root/flourisha/00_AI_Brain/skills/my-skill
# ... create SKILL.md here ...
```

---

## Skill Structure

Every skill should follow this structure:

```
/root/flourisha/00_AI_Brain/skills/skill-name/
├── SKILL.md                    # Main skill definition (required)
├── skill-card.json            # A2A capability declaration (optional)
├── examples/                  # Usage examples (optional)
│   └── example-1.md
├── workflows/                 # Workflows/processes (optional)
├── templates/                 # Templates for skill output (optional)
├── docs/                      # Extended documentation (optional)
└── scripts/                   # Scripts for skill execution (optional)
```

---

## SKILL.md Template

Every skill MUST have a `SKILL.md` at the root of its directory:

```markdown
---
name: Skill Name
description: What this skill does
tags: [tag1, tag2]
color: blue
---

# Skill Name

Your skill documentation here.
```

---

## Verification Checklist

When you create or modify a skill:

- [ ] Skill is in `/root/flourisha/00_AI_Brain/skills/skill-name/`
- [ ] NOT in `/root/.claude/skills/skill-name/` directly
- [ ] `SKILL.md` exists at skill root
- [ ] Skill is accessible via `/root/.claude/skills/skill-name/` (through symlink)
- [ ] If Git-tracked: committed to correct location
- [ ] If in Flourisha drive: synced via `flourisha-sync`

---

## Implementation Checklist

### Phase 1: Documentation & Awareness ✅
- [x] This document created
- [ ] Share with all developers working with skills
- [ ] Add to `README.md` as reference

### Phase 2: Automation (Optional)
- [ ] Create pre-commit hook at `/root/flourisha/00_AI_Brain/hooks/skills-unification-check.sh`
- [ ] Install hook into git pre-commit
- [ ] Test hook prevents accidental `.claude/skills/` commits

### Phase 3: File System Protection (Optional)
- [ ] Change `.claude/skills/` permissions to read-only
- [ ] Document reason for restricted permissions

### Phase 4: Cleanup & Sync
- [ ] Run final audit for any divergences
- [ ] Sync everything to Google Drive
- [ ] Update Git remotes

---

## FAQ

**Q: But I see files in `/root/.claude/skills/`?**
A: Those are the same files - you're seeing them through the symlink. Try: `ls -la /root/.claude/skills/` - notice the first symlink entry.

**Q: What if I created something in `.claude/skills/` by accident?**
A: No problem! The symlink makes it harmless - it's actually in the Flourisha directory. Just remember for next time to work directly in `/root/flourisha/00_AI_Brain/skills/`.

**Q: Can I edit skills through the symlink?**
A: Yes, it works fine for reading and editing. But to be clear about intent, work in the actual directory: `/root/flourisha/00_AI_Brain/skills/`.

**Q: What about Google Drive syncing?**
A: Google Drive only syncs the real directory (`/root/flourisha/`), not the symlink. This is fine - everything ends up in the right place.

**Q: Why not just delete the `.claude/skills/` symlink?**
A: Claude Code expects it there for backward compatibility. Keep the symlink; just ensure new work goes to the real location.

---

## Symlink Verification

To verify the symlink is still working:

```bash
# This should show it's a symlink pointing to flourisha
ls -la /root/.claude/skills

# This should list all skills
ls /root/.claude/skills/

# This should access the same skill through both paths
diff -r /root/.claude/skills/CORE /root/flourisha/00_AI_Brain/skills/CORE
# Should output nothing (identical)
```

---

## When to Apply This Strategy

**Immediately:**
- All new skill creation must follow this
- Existing developers informed

**Cleanup:**
- After next major update/sync
- Document any migration of legacy skills

**Enforcement:**
- Use pre-commit hook for Git commits
- Make `.claude/skills/` read-only after 30 days grace period

---

## Related Documentation

- **Skills System:** See `/root/flourisha/00_AI_Brain/documentation/` for skill management
- **AI Brain Structure:** See `FLOURISHA_AI_ARCHITECTURE.md`
- **A2A Protocol:** See `A2A_IMPLEMENTATION_COMPLETE.md`

---

**Last Updated:** 2025-12-04
**Owner:** Flourisha AI Infrastructure
**Review Schedule:** Quarterly
