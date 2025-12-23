# Flourisha Google Drive Sync Commands

**Quick Reference for syncing `/root/flourisha/` with Google Drive**

---

## Primary Commands (Use These)

### flourisha-push
**Push local changes to Google Drive**
```bash
flourisha-push
```
- Uploads local changes from `/root/flourisha/` to Google Drive
- One-way sync: server → Google Drive
- Safe: won't delete anything on server

### flourisha-pull
**Pull changes from Google Drive to server**
```bash
flourisha-pull
```
- Downloads changes from Google Drive to `/root/flourisha/`
- One-way sync: Google Drive → server
- Safe: won't delete anything on Drive

### flourisha-sync
**Bidirectional sync (use with caution)**
```bash
flourisha-sync
```
- Two-way sync between server and Google Drive
- Newer files win on both sides
- Use when editing from multiple locations

### sync-status
**Check sync status**
```bash
sync-status
```
- Shows what's different between server and Drive
- Useful before running sync commands

---

## Navigation Commands

### flourisha
**Navigate to Flourisha directory**
```bash
flourisha
# Same as: cd /root/flourisha
```

---


---

## Common Workflows

### After Editing on Server
```bash
# Made changes to skills/docs on server
flourisha-push
# Now changes are in Google Drive and Obsidian
```

### After Editing in Obsidian
```bash
# Edited files in Obsidian (Windows)
# Google Drive auto-syncs from Windows
# On server:
flourisha-pull
# Now server has your Obsidian changes
```

### Working on AI Brain
```bash
# Navigate to AI Brain
flourisha
cd 00_AI_Brain

# Edit some files
nano skills/research/SKILL.md

# Push to Drive
flourisha-push

# Later, from another machine, edited in Obsidian
# Back on server:
flourisha-pull
```

### Check Before Syncing
```bash
# See what's different
sync-status

# Decide which direction to sync
flourisha-push  # or flourisha-pull
```

---

## Safety Tips

### Before Pulling
If you have local changes:
```bash
sync-status  # See what will change
flourisha-push  # Push your changes first
flourisha-pull  # Then pull Drive changes
```

### Before Pushing
If you edited in Obsidian:
```bash
sync-status  # See what's different
flourisha-pull  # Get Drive changes first
# Then make your server edits
flourisha-push  # Push combined changes
```

### Bidirectional Sync
Only use `flourisha-sync` when:
- You edited on both server AND Obsidian
- You want newer files to win on both sides
- You're comfortable with automatic conflict resolution

---

## Under the Hood

**Scripts Location:**
```bash
/root/.claude/scripts/flourisha_push.sh      # flourisha-push
/root/.claude/scripts/flourisha_sync.sh      # flourisha-pull
/root/.claude/scripts/flourisha_bisync.sh    # flourisha-sync
/root/.claude/scripts/flourisha_sync_status.sh  # sync-status
```

**Google Drive:**
- Remote name: `Flourisha_gDrive`
- Shared drive on Google Drive
- Appears at `G:\Shared drives\Flourisha_gDrive` on Windows

**Local Path:**
- `/root/flourisha/`

**What Gets Synced:**
- Everything in `/root/flourisha/`
- Including `00_AI_Brain/` (all skills, docs, scripts)
- PARA folders (01f, 02f, 03f, 04f)

---

## Troubleshooting

### "No changes detected"
Good! Everything is already synced.

### "Permission denied"
Check rclone config:
```bash
rclone listremotes
# Should show: Flourisha_gDrive:
```

### "Conflict: both modified"
Use `sync-status` to see conflicts, then:
```bash
# Option 1: Server wins
flourisha-push

# Option 2: Drive wins
flourisha-pull

# Option 3: Newer wins (both directions)
flourisha-sync
```

### Check what will change
```bash
# Dry run (don't actually sync)
rclone sync /root/flourisha Flourisha_gDrive: --dry-run
```

---

## Quick Reference Card

| Command | Direction | Use When |
|---------|-----------|----------|
| `flourisha-push` | Server → Drive | Edited on server |
| `flourisha-pull` | Drive → Server | Edited in Obsidian |
| `flourisha-sync` | Both ways | Edited both places |
| `sync-status` | Check only | Want to see differences |
| `flourisha` | Navigate | Go to /root/flourisha |

---

**Best Practice:**
1. Edit in one place at a time
2. Use `flourisha-push` after server edits
3. Use `flourisha-pull` after Obsidian edits
4. Check `sync-status` when unsure

---

**Created:** 2025-11-19
**Location:** `/root/flourisha/00_AI_Brain/SYNC_COMMANDS.md`
