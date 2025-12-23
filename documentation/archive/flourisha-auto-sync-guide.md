# Flourisha Auto-Sync Guide

## Overview

Automatic bi-directional synchronization between `/root/flourisha/` (local server) and Google Drive `Flourisha_gDrive` shared drive.

**Status:** ✅ Active and Running

---

## How It Works

1. **File Watching:** `inotifywait` monitors `/root/flourisha/` recursively for:
   - File modifications (saves)
   - New file creation
   - File deletions
   - File moves/renames

2. **Smart Debouncing:**
   - Waits 60 seconds after the last file change
   - Prevents syncing during active editing
   - Batches multiple changes into single sync

3. **File Lock Detection:**
   - Uses `lsof` and `fuser` to check if files are open
   - Delays sync if files are still being edited
   - Reschedules automatically when files close

4. **Sync Execution:**
   - Pushes changes to Google Drive using `rclone copy`
   - One-way sync: server → Google Drive
   - Preserves all files (doesn't delete)

5. **Automatic Recovery:**
   - Systemd manages the service
   - Auto-restarts on failure
   - Starts on server boot

---

## Management Commands

### Quick Status Check
```bash
sync-status
```

### View Live Logs
```bash
sync-status logs
```

### Service Control
```bash
sync-status start    # Start the service
sync-status stop     # Stop the service
sync-status restart  # Restart the service
```

### Test the Sync
```bash
sync-status test     # Creates a test file
```

### Manual Sync (if needed)
```bash
flourisha-pull   # Pull from Google Drive → local
flourisha-push   # Push from local → Google Drive
```

---

## What Gets Synced

**Included:**
- All files in `/root/flourisha/`
- All PARA folders (Projects, Areas, Resources, Archives)
- Markdown files, PDFs, images, etc.

**Excluded:**
- `.obsidian/` (Obsidian app data)
- `.trash/` (trash folder)
- `.DS_Store` (macOS metadata)
- `*.tmp`, `*.swp` (temporary files)
- `.git/` (git repositories)

---

## Service Details

**Service Name:** `flourisha-auto-sync.service`

**Script Location:** `/root/.claude/scripts/flourisha_auto_sync.sh`

**Log File:** `/var/log/pai_auto_sync.log`

**Debounce Period:** 60 seconds

**Remote:** `flourisha:` → Google Drive Shared Drive "Flourisha_gDrive"

---

## Typical Workflow

1. **You edit a file in Obsidian (Windows):**
   - Save the file
   - Google Drive desktop sync pushes to cloud
   - Server pulls with `flourisha-pull` (manual)

2. **AI creates/modifies a file on server:**
   - File is saved to `/root/flourisha/`
   - Auto-sync detects the change
   - Waits 60 seconds (debounce)
   - Checks file isn't locked
   - Pushes to Google Drive automatically
   - Available in Obsidian within minutes

3. **Multiple rapid edits:**
   - All changes batched together
   - Single sync after 60 seconds of inactivity
   - Efficient and prevents spam

---

## Monitoring

### Check Service Status
```bash
systemctl status flourisha-auto-sync.service
```

### View Recent Activity
```bash
tail -f /var/log/pai_auto_sync.log
```

### Check What's Being Watched
```bash
sync-status status
```

---

## Troubleshooting

### Sync Not Working

1. **Check service is running:**
   ```bash
   sync-status status
   ```

2. **Check logs for errors:**
   ```bash
   tail -50 /var/log/pai_auto_sync.log
   ```

3. **Restart service:**
   ```bash
   sync-status restart
   ```

### Files Not Syncing

1. **Check if file is excluded:**
   - Temp files (*.tmp, *.swp) are excluded
   - Hidden folders (.obsidian, .trash) are excluded

2. **Check debounce timer:**
   - Wait 60+ seconds after file change
   - Check logs to see if sync scheduled

3. **Check file locks:**
   - Close file in editor
   - Wait for sync to proceed

### High CPU Usage

- Normal during initial sync or large file changes
- Should idle when no changes occurring
- Check logs for sync loops

---

## Advanced Configuration

### Change Debounce Period

Edit `/root/.claude/scripts/flourisha_auto_sync.sh`:
```bash
DEBOUNCE_SECONDS=60  # Change to desired seconds
```

Then restart:
```bash
sync-status restart
```

### Add Exclusions

Edit the `--exclude` patterns in the script:
```bash
--exclude "your-pattern/**"
```

### Disable Auto-Sync

```bash
sync-status stop
sync-status disable
```

To re-enable:
```bash
sync-status enable
sync-status start
```

---

## Files and Locations

| Item | Location |
|------|----------|
| Watch Directory | `/root/flourisha/` |
| Auto-Sync Script | `/root/.claude/scripts/flourisha_auto_sync.sh` |
| Status Script | `/root/.claude/scripts/flourisha_sync_status.sh` |
| Systemd Service | `/etc/systemd/system/flourisha-auto-sync.service` |
| Log File | `/var/log/pai_auto_sync.log` |
| Bidirectional Sync | `/root/.claude/scripts/flourisha-sync.sh` |

---

## Security Notes

- Service runs as root (required for full file access)
- Uses secure rclone authentication
- Logs all sync operations
- No external access to watch directory
- Google Drive OAuth tokens stored securely

---

## Performance

- **Idle resource usage:** Minimal (<1% CPU, ~5MB RAM)
- **During sync:** Moderate (depends on file size)
- **Network usage:** Only when syncing changes
- **Sync speed:** ~60 KB/s (varies with connection)

---

## Support

For issues or questions:
1. Check logs: `/var/log/pai_auto_sync.log`
2. Check service status: `sync-status`
3. Test manually: `sync-status test`
4. Review this guide
5. Ask Flourisha for help

---

**Last Updated:** 2025-11-17
**Version:** 1.0
**Status:** Production - Active
