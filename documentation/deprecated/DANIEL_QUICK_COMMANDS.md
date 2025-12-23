# Daniel's PAI - Quick Command Reference

**Purpose:** Copy-paste commands for integrating Daniel's PAI files

---

## 🔄 Update Staging Folder

```bash
# Pull latest from Daniel
cd /root/pai
git fetch origin
git reset --hard origin/main

# Check what changed
git log -1 --stat
```

---

## 🔍 Check for Sensitive Data

**Before pulling ANY file, run this:**

```bash
# Single file check
FILE="/root/pai/.claude/skills/CORE/CONSTITUTION.md"
grep -E "sk-|api_key|ANTHROPIC_API_KEY|@gmail|@yahoo|password|secret|credential" "$FILE"

# All files in a directory
grep -r -E "sk-|api_key|@gmail|password|secret" /root/pai/.claude/skills/
```

✅ No output = Safe to pull
❌ Matches found = Review and sanitize first

---

## 📋 Copy File Safely

```bash
# Template
cp /root/pai/SOURCE_PATH/filename.md \
   /root/flourisha/00_AI_Brain/documentation/REFERENCE_filename.md

# Example 1: CONSTITUTION
cp /root/pai/.claude/skills/CORE/CONSTITUTION.md \
   /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md

# Example 2: SECURITY
cp /root/pai/SECURITY.md \
   /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_SECURITY.md

# Example 3: Hook system
cp /root/pai/.claude/skills/CORE/hook-system.md \
   /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_HOOK_SYSTEM.md
```

---

## 📝 Add Source Header to File

**After copying, edit the file and add this at the top:**

```markdown
# [Original Title] (Reference)

**Source:** Daniel's Personal AI Infrastructure
**Repository:** https://github.com/danielmiessler/Personal_AI_Infrastructure
**Last Synced:** 2025-12-04
**Status:** Reference documentation - Study only, don't execute directly
**Adapted For:** Flourisha Personal AI System

---

[Original content continues below]
```

---

## 📚 View Files You're Considering

```bash
# Read a file you're thinking about pulling
less /root/pai/.claude/skills/CORE/CONSTITUTION.md

# Or with line numbers
cat -n /root/pai/.claude/skills/CORE/CONSTITUTION.md | less

# Search within file
grep -n "founding\|principle\|philosophy" /root/pai/.claude/skills/CORE/CONSTITUTION.md
```

---

## 📂 List Files Available to Pull

```bash
# All CORE skills
ls -la /root/pai/.claude/skills/CORE/

# All documentation in root
ls -la /root/pai/*.md

# All skills
find /root/pai/.claude/skills -name "*.md" | head -20

# All hooks
ls -la /root/pai/.claude/hooks/
```

---

## 🔐 Sanitization Examples

### Example: Remove Personal Email

**Before:**
```markdown
Contact: daniel@danielmiessler.com
Author: daniel
```

**After:**
```markdown
Contact: your-email@example.com
Author: [Your Name]
```

### Example: Remove API Key

**Before:**
```bash
ANTHROPIC_API_KEY=sk-ant-1234567890abcdef
```

**After:**
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Example: Replace File Paths

**Before:**
```bash
PAI_DIR="/Users/daniel/Projects/PAI"
hooks_dir="${PAI_DIR}/hooks"
```

**After:**
```bash
PAI_DIR="/root/flourisha/00_AI_Brain"
hooks_dir="${PAI_DIR}/hooks"
```

---

## 📖 Compare Files

```bash
# Compare file from Daniel with yours
diff /root/pai/SECURITY.md /root/flourisha/00_AI_Brain/documentation/security/SECURITY.md

# Compare directories
diff -r /root/pai/.claude/skills/CORE /root/flourisha/00_AI_Brain/skills/CORE

# Show differences with context
diff -u /root/pai/FILE.md /root/flourisha/00_AI_Brain/documentation/FILE.md | less
```

---

## ✅ Validation After Pulling

```bash
# 1. Verify file was copied
ls -la /root/flourisha/00_AI_Brain/documentation/REFERENCE_*.md

# 2. Check file size is reasonable
wc -l /root/flourisha/00_AI_Brain/documentation/REFERENCE_*.md

# 3. Search for any missed sensitive data
grep -r -E "sk-|api_key|@gmail|password" /root/flourisha/00_AI_Brain/documentation/REFERENCE_*

# 4. Verify source header is there
head -10 /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md
```

---

## 📊 Documentation Maintenance

```bash
# View your documentation index
cat /root/flourisha/00_AI_Brain/documentation/README.md

# Edit documentation index (add new file entry)
nano /root/flourisha/00_AI_Brain/documentation/README.md

# Update the integration log
nano /root/flourisha/00_AI_Brain/documentation/DANIEL_PAI_MERGE_STRATEGY.md
# Find "Current Integration Log" section and add entry
```

---

## 🎯 Phase 1: This Week (Study Mode)

```bash
# Step 1: Read key files
echo "=== Reading CONSTITUTION.md ==="
less /root/pai/.claude/skills/CORE/CONSTITUTION.md

echo "=== Reading SECURITY.md ==="
less /root/pai/SECURITY.md

echo "=== Reading PAI_SYNC_GUIDE.md ==="
less /root/pai/PAI_SYNC_GUIDE.md

echo "=== Reading hook-system.md ==="
less /root/pai/.claude/skills/CORE/hook-system.md
```

---

## 🚀 Phase 2: Next 2 Weeks (Selective Pulling)

```bash
# Step 1: Check for sensitive data
echo "Checking CONSTITUTION.md for sensitive data..."
grep -E "sk-|@gmail|password" /root/pai/.claude/skills/CORE/CONSTITUTION.md && \
  echo "❌ SENSITIVE DATA FOUND" || echo "✅ SAFE TO PULL"

# Step 2: Copy CONSTITUTION.md
cp /root/pai/.claude/skills/CORE/CONSTITUTION.md \
   /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md

# Step 3: Edit to add source header
nano /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md

# Step 4: Verify copy
ls -lh /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md

# Step 5: Update documentation index
nano /root/flourisha/00_AI_Brain/documentation/README.md
# Add entry under "Reference Guides" section

# Step 6: Update integration log
nano /root/flourisha/00_AI_Brain/documentation/DANIEL_PAI_MERGE_STRATEGY.md
# Add row to integration log table
```

---

## 📝 Quick Checklists

### Before Pulling File
- [ ] Read the file first
- [ ] Checked for API keys (grep sk-)
- [ ] Checked for emails (grep @gmail/@yahoo)
- [ ] Checked for passwords (grep password/secret)
- [ ] Checked git history (git log)
- [ ] Know where it will go

### After Pulling File
- [ ] File copied to correct location
- [ ] Source header added
- [ ] No sensitive data remaining
- [ ] Documentation index updated
- [ ] Integration log updated
- [ ] Verified file integrity

---

## 🔗 Key Locations

```bash
# Daniel's PAI (staging)
/root/pai/

# Your AI Brain (source of truth)
/root/flourisha/00_AI_Brain/

# Strategy documents you created
/root/flourisha/00_AI_Brain/documentation/DANIEL_*.md

# CORE skills (Daniel's)
/root/pai/.claude/skills/CORE/

# Your CORE skill
/root/flourisha/00_AI_Brain/skills/CORE/

# Documentation folder
/root/flourisha/00_AI_Brain/documentation/

# Integration log location
/root/flourisha/00_AI_Brain/documentation/DANIEL_PAI_MERGE_STRATEGY.md
```

---

## 📞 Troubleshooting

### "Command not found" when trying flourisha-bisync
```bash
# Try checking for sync command
ls -la /root/.bashrc
# Check if alias is defined there

# For now, manually copy to Google Drive or skip sync
```

### "File already exists" error
```bash
# Check if file already exists
ls /root/flourisha/00_AI_Brain/documentation/REFERENCE_DANIEL_CONSTITUTION.md

# If it does, either:
# 1. Update it: cp with -f flag
# 2. Rename the new one differently
```

### "Permission denied"
```bash
# Check file permissions
ls -la /root/flourisha/00_AI_Brain/documentation/

# Fix permissions if needed
chmod 644 /root/flourisha/00_AI_Brain/documentation/filename.md
```

---

## ⏱️ Time Tracking

Use this to log how long integration takes:

```
Week 1:
- Study Phase: _____ minutes
- Total: _____ hours

Week 2-3:
- Pull Phase: _____ minutes
- Total: _____ hours

Notes:
- Most valuable file: _________________
- Least useful: _________________
- Time saved learning from Daniel: _________________
```

---

## 🎓 Learning Outcomes

After this integration, you should understand:

- [ ] Daniel's 8 founding principles
- [ ] How to safely sync public/private systems
- [ ] Prompt injection defense patterns
- [ ] Hook system architecture
- [ ] Best practices for prompting
- [ ] How to document for public consumption

---

**Copy these commands into your terminal as needed. All paths are absolute, so they work from any directory.**
