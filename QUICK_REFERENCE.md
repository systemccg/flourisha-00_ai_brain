# Flourisha AI Brain - Quick Reference

**Version:** 1.0 | **Date:** 2025-11-19

---

## 📍 Key Locations

```
AI Brain:     /root/flourisha/00_AI_Brain/
Skills:       /root/flourisha/00_AI_Brain/skills/
Docs:         /root/flourisha/00_AI_Brain/documentation/
Scripts:      /root/flourisha/00_AI_Brain/scripts/
Context:      /root/flourisha/00_AI_Brain/context/

Claude:       /root/.claude/skills → (symlink to AI Brain)
Gemini:       /root/.gemini/skills → (future)
```

---

## 🚀 Quick Commands

### Navigate
```bash
cd /root/flourisha/00_AI_Brain        # Go to AI Brain
cd /root/flourisha/00_AI_Brain/skills # Browse skills
```

### Read Context
```bash
cat /root/flourisha/00_AI_Brain/context/MASTER_CONTEXT.md
cat /root/flourisha/00_AI_Brain/documentation/README.md
```

### List Content
```bash
ls -la /root/flourisha/00_AI_Brain/skills/     # All skills
ls -la /root/flourisha/00_AI_Brain/documentation/       # All docs
ls -la /root/flourisha/00_AI_Brain/scripts/    # All scripts
```

### Start Services
```bash
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --list
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --services neo4j
```

### Google Drive Sync
```bash
flourisha-push   # Upload to Google Drive
flourisha-pull   # Download from Google Drive
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | AI Brain overview |
| [context/MASTER_CONTEXT.md](context/MASTER_CONTEXT.md) | System facts |
| [docs/README.md](docs/README.md) | Doc index |
| [docs/startup/services.md](docs/startup/services.md) | Service startup |
| [docs/monitoring/overview.md](docs/monitoring/overview.md) | Monitoring |
| [docs/security/scanning.md](docs/security/scanning.md) | Security |

---

## 🎯 Skills Structure

```
skill-name/
├── SKILL.md         # Core definition
├── workflows/       # Specific tasks
├── assets/          # Templates
├── examples/        # Example outputs
└── scripts/         # Helper scripts
```

**All 13 skills:** CORE, research, fabric, ffuf, prompting, agent-observability, alex-hormozi-pitch, create-skill, deal-pipeline, example-skill, financial-analysis, property-management, real-estate-core

---

## 🔗 Symlinks

```bash
# Verify Claude can access skills
ls -la /root/.claude/skills
# Should show: skills -> /root/flourisha/00_AI_Brain/skills

# Test access
cat /root/.claude/skills/research/SKILL.md
```

---

## 🖥️ Obsidian Access

**Windows Path:**
```
G:\Shared drives\Flourisha_gDrive\00_AI_Brain\
```

**Workflow:**
1. Edit in Obsidian (Windows)
2. Auto-syncs to Google Drive
3. Run `flourisha-pull` on server
4. Changes appear immediately

---

## ✅ Verification

```bash
# Check structure
ls -la /root/flourisha/00_AI_Brain/

# Count skills
ls -1 /root/flourisha/00_AI_Brain/skills/ | wc -l

# Verify examples in all skills
find /root/flourisha/00_AI_Brain/skills -name "examples" -type d | wc -l

# Test symlink
test -L /root/.claude/skills && echo "Symlink OK" || echo "Problem!"
```

---

## 🆘 Troubleshooting

**Skills not found?**
```bash
ls -la /root/.claude/skills  # Check symlink exists
```

**Sync not working?**
```bash
rclone lsd Flourisha_gDrive:  # Check Drive connection
```

**Need to restore?**
```bash
# Original skills backed up at:
ls /root/.claude/skills.backup.20251119/
```

---

## 📊 Implementation Stats

- ✅ **13 skills** migrated
- ✅ **5 docs** centralized
- ✅ **9 scripts** organized
- ✅ **15 examples/** directories added
- ✅ **1 master context** created
- ✅ **1 symlink** working
- ✅ **100%** backward compatible

---

**Full Docs:** `/root/FLOURISHA_AI_ARCHITECTURE.md`
**Implementation:** `/root/IMPLEMENTATION_COMPLETE.md`
