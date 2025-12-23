# Flourisha Google Drive Sync - Simple Guide

**Last Updated:** 2025-11-19
**Method:** Bidirectional Sync (rclone bisync)

---

## 🎯 One Command to Rule Them All

```bash
flourisha-sync
```

That's it. Use this command to keep Google Drive and local server in sync.

---

## 📖 How It Works

**Bidirectional Sync** means changes flow both ways automatically:

- ✅ New files on Google Drive → Downloaded to server
- ✅ New files on server → Uploaded to Google Drive
- ✅ Deleted files on either side → Deleted from other side
- ✅ Modified files → Newer version wins
- ✅ Conflicts → Both versions kept (.conflict-1, .conflict-2)

---

## 🚀 Daily Usage

### Before Starting Work
```bash
flourisha-sync
```

### After Making Changes (Optional)
```bash
flourisha-sync
```

**Note:** You can run this as often as you want. It's smart enough to only sync what changed.

---

## 🧪 Testing Mode

Test changes in isolated folder first:

```bash
flourisha-sync --test --dry-run    # Preview what would happen
flourisha-sync --test              # Actually sync test folder
```

This uses `/root/flourisha/00_SYNC_TEST/` only.

---

## 🔍 Dry Run (Preview)

See what would change without actually changing it:

```bash
flourisha-sync --dry-run
```

---

## 🔄 First Time Setup (Already Done)

The sync was initialized on 2025-11-19. You don't need to do this again unless you want to reset:

```bash
flourisha-sync --resync    # Re-initialize sync state
```

**Warning:** Only use `--resync` if:
- Sync is broken and won't run
- You moved/renamed many files manually
- Bisync reports errors and asks for resync

---

## 🛡️ What's Excluded from Sync

Automatically excluded (via `/root/flourisha/.rclone-filter`):

- `node_modules/` - All Node.js dependencies
- `__pycache__/`, `*.pyc` - Python bytecode
- `.git/` - Git repositories
- `dist/`, `build/`, `.next/` - Build artifacts
- `.vscode/`, `.idea/` - IDE files
- `*.db`, `*.sqlite` - Database files
- Large GIF files (>10MB)
- Temp files (`.tmp`, `.log`, `.cache`)

Also excluded (via script):
- `.obsidian/**` - Obsidian workspace (local only)
- `ToBeDeleted/**` - Backup directory
- `**/*.CONFLICT-*` - Conflict files

---

## 📊 What Gets Synced

Everything else in `/root/flourisha/` including:

- `00_AI_Brain/` - AI agents, skills, documentation, scripts
- `01f_Flourisha_Projects/` - Active projects
- `02f_Flourisha_Areas/` - Areas of responsibility
- `03f_Flourisha_Resources/` - Reference materials
- `04f_Flourisha_Archives/` - Archived items
- All markdown files, configs, and source code

---

## 🚨 If Sync Fails

### Error: "Bisync needs initialization"
```bash
flourisha-sync --resync
```

### Error: "Path1 and Path2 are not in sync"
This means files changed on both sides. Options:

1. **Keep both versions (recommended):**
   ```bash
   flourisha-sync    # Will create .conflict-1, .conflict-2 files
   ```

2. **Force resync (nuclear option):**
   ```bash
   flourisha-sync --resync
   ```
   ⚠️ This may lose some sync history

### Error: "Lock file exists"
Another sync is running. Wait or:
```bash
rm -f /tmp/flourisha_bisync.lock
flourisha-sync
```

---

## 🎓 Advanced Options

```bash
# Full command syntax
bash /root/.claude/scripts/flourisha_bisync.sh [OPTIONS]

Options:
  --dry-run    Preview changes without making them
  --test       Use test folder only (00_SYNC_TEST)
  --resync     Re-initialize bisync state
```

---

## 💡 Tips

1. **Sync often:** Run `flourisha-sync` whenever you switch contexts (work on server → work in Obsidian)

2. **Check conflicts:** If you see `.conflict-1` or `.conflict-2` files, review and keep the one you want

3. **Test first:** When unsure, use `--dry-run` to preview

4. **Obsidian workflow:**
   - Work in Obsidian on Windows (directly on Google Drive)
   - Run `flourisha-sync` on server to get latest
   - Work on server with PAI
   - Sync happens automatically on next run

5. **Don't worry about deletions:** Deleted files are backed up to `ToBeDeleted/` for 30 days (on both sides)

---

## 📁 Folder Structure

```
/root/flourisha/                  ← Local working directory
└── syncs with ↓

Google Drive: Flourisha_gDrive    ← Cloud storage
└── syncs with ↓

G:\Shared drives\Flourisha_gDrive ← Obsidian on Windows
```

All three stay in sync automatically.

---

## 🔗 Aliases Available

```bash
flourisha-sync     # Main command
flourisha-bisync   # Same thing
```

Both run the same script: `/root/.claude/scripts/flourisha_bisync.sh`

---

## 📝 Log Files

Check what happened:
```bash
tail -f /var/log/pai_flourisha_bisync.log
```

---

## ✅ Quick Reference Card

| Task | Command |
|------|---------|
| Sync everything | `flourisha-sync` |
| Preview changes | `flourisha-sync --dry-run` |
| Test mode | `flourisha-sync --test` |
| Re-initialize | `flourisha-sync --resync` |
| Check logs | `tail /var/log/pai_flourisha_bisync.log` |

---

**That's it!** One command, bidirectional sync, automatic conflict resolution. Simple. 🚀

---

**See also:**
- `/root/flourisha/00_AI_Brain/SYNC_RECOVERY_AND_SAFETY.md` - Recovery procedures
- `/root/flourisha/00_AI_Brain/SYNC_OPTIMIZATION_COMPLETE.md` - Optimization details
- `/root/flourisha/.rclone-filter` - Exclusion rules
