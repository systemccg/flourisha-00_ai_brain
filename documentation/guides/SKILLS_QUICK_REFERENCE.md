# Skills - Quick Reference

**Single Source of Truth:** `/root/flourisha/00_AI_Brain/skills/`

---

## Where to Work

✅ **CREATE** new skills here:
```bash
/root/flourisha/00_AI_Brain/skills/skill-name/
```

✅ **EDIT** skills here:
```bash
/root/flourisha/00_AI_Brain/skills/skill-name/SKILL.md
```

❌ **DON'T** work in:
```bash
/root/.claude/skills/  # This is a symlink (read-only reference)
```

---

## New Skill Creation

```bash
# 1. Create directory in Flourisha
mkdir -p /root/flourisha/00_AI_Brain/skills/my-new-skill

# 2. Create SKILL.md
cat > /root/flourisha/00_AI_Brain/skills/my-new-skill/SKILL.md << 'EOF'
---
name: My New Skill
description: What this skill does
tags: [tag1, tag2]
color: blue
---

# My New Skill

Your documentation here.
EOF

# 3. Create skill-card.json (optional, for A2A)
cat > /root/flourisha/00_AI_Brain/skills/my-new-skill/skill-card.json << 'EOF'
{
  "id": "my-new-skill",
  "name": "My New Skill",
  "version": "1.0.0",
  "description": "What this skill does"
}
EOF

# 4. Verify it's accessible through symlink
ls /root/.claude/skills/my-new-skill/

# 5. Commit to Git (if in repo)
git add flourisha/00_AI_Board/skills/my-new-skill/
git commit -m "Add my-new-skill"

# 6. Sync to Google Drive (if applicable)
flourisha-sync
```

---

## Skill File Structure

```
skill-name/
├── SKILL.md                    # Required: Main skill definition
├── skill-card.json            # Optional: A2A declaration
├── examples/                  # Optional: Usage examples
│   └── example-1.md
├── workflows/                 # Optional: Workflows
├── templates/                 # Optional: Output templates
├── docs/                      # Optional: Extended docs
└── scripts/                   # Optional: Automation scripts
```

---

## Accessing Skills

**Via Flourisha (source):**
```bash
ls /root/flourisha/00_AI_Brain/skills/
cd /root/flourisha/00_AI_Brain/skills/my-skill/
```

**Via Claude symlink (convenient):**
```bash
ls /root/.claude/skills/
cd /root/.claude/skills/my-skill/  # Same as above!
```

Both paths work. Use Flourisha path for clarity.

---

## Troubleshooting

**Q: I can't find my skill in `.claude/skills/`**
A: Did you create it directly there? Move it:
```bash
# If you created it in wrong place
cp -r /root/.claude/skills/my-skill /root/flourisha/00_AI_Brain/skills/
```

**Q: The symlink is broken**
A: Verify it exists:
```bash
ls -la /root/.claude/skills
# Should show: skills -> /root/flourisha/00_AI_Board/skills
```

If missing, recreate:
```bash
cd /root/.claude
rm skills  # If it exists but is wrong
ln -s /root/flourisha/00_AI_Brain/skills skills
```

**Q: Two copies of my skill exist**
A: Keep the one in Flourisha, delete the one in `.claude/skills/`:
```bash
rm -rf /root/.claude/skills/my-skill
# Via symlink, this removes from Flourisha too... so recreate:
mkdir -p /root/flourisha/00_AI_Brain/skills/my-skill
# Add your files back
```

---

## Git Pre-Commit Hook

Prevents accidental commits to `.claude/skills/`:

```bash
# Install hook
cp /root/flourisha/00_AI_Brain/hooks/skills-unification-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test it works (this will fail as expected)
touch /root/.claude/skills/test-file.txt
git add .claude/skills/test-file.txt
git commit -m "test"  # Should be rejected
```

---

## See Also

- **Full Strategy:** `/root/flourisha/00_AI_Brain/documentation/SKILLS_UNIFICATION_STRATEGY.md`
- **AI Brain Docs:** `/root/flourisha/00_AI_Brain/documentation/README.md`
- **A2A Integration:** `/root/flourisha/00_AI_Brain/documentation/A2A_IMPLEMENTATION_COMPLETE.md`
