---
name: flourisha-sync
description: Sync Flourisha directory to Google Drive via rclone bisync. Automatically excludes node_modules and venv directories for optimal performance. USE WHEN user says 'sync flourisha', 'sync to google drive', 'flourisha-sync', 'run bisync', or 'push to drive'.
---

# Flourisha-Sync Skill

Bidirectional synchronization of your Flourisha directory to Google Drive using rclone bisync.

## When to Activate

- User requests: "sync flourisha"
- User requests: "sync to google drive"
- User requests: "run flourisha-bisync"
- Daily automated sync scheduled
- Before major operations to ensure Google Drive is up-to-date

## Core Workflow

### Step 1: Pre-Sync Checks (15 seconds)

1. **Check for stale lock file**
   ```bash
   ls -la /root/.cache/rclone/bisync/root_flourisha..flourisha_.lck 2>/dev/null
   ```
   - If exists and > 5 minutes old: Delete it
   ```bash
   rclone deletefile "/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck"
   ```

2. **Verify rclone remote exists**
   ```bash
   rclone listremotes | grep -q "^flourisha:"
   ```

### Step 2: Execute Sync (2-5 minutes)

Run bisync with exclusions:
```bash
rclone bisync /root/flourisha flourisha: \
  --exclude "node_modules/" \
  --exclude "venv/" \
  --exclude ".venv/" \
  --exclude "**/node_modules/" \
  --exclude "**/venv/" \
  --resync \
  --interactive=false
```

**Exclusions explained:**
- `node_modules/` - NPM/Yarn dependencies (not needed in cloud)
- `venv/` - Python virtual environments (recreatable)
- `.venv/` - Alternative venv directory name
- `**/` prefix - Catches these directories at any nesting level

### Step 3: Monitor Sync (Real-time)

1. Display progress messages
2. Track key metrics:
   - Files scanned
   - Files transferred
   - Errors encountered
   - Duration

### Step 4: Post-Sync Validation (15 seconds)

1. **Check exit code** - Confirm sync completed successfully
2. **Verify sync completion** - Check for success message in output
3. **Report summary** to user:
   - Total files processed
   - Sync direction (local → cloud, cloud → local, both)
   - Any conflicts or skipped items
   - Total time elapsed

## Parameters

Optional command modifiers:
- `--force` - Skip lock file checks and force sync
- `--no-exclude` - Include everything (not recommended)
- `--dry-run` - Show what would sync without actually syncing

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Lock file exists | Previous sync interrupted | Delete lock file (auto-handled) |
| Remote not found | rclone not configured | Check `rclone config list` |
| Permission denied | Google Drive auth expired | Re-authenticate: `rclone authorize drive` |
| Duplicate objects | Files exist in both places | bisync handles automatically with --resync |
| Symlink errors | Can't follow symlinks | Expected warnings - not errors, skipped safely |

## Daily Automation

The sync runs automatically via cron job. Verify with:
```bash
crontab -l | grep flourisha
```

Expected output:
```
0 2 * * * /root/.claude/skills/flourisha-sync/sync-runner.sh >> /var/log/flourisha-sync.log 2>&1
```

This runs daily at 2 AM UTC.

## Usage Examples

### Example 1: Manual Sync (User Request)

**Trigger:** User says "sync flourisha to google drive"

```bash
# Check for lock file
if [ -f "/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck" ]; then
  rclone deletefile "/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck"
fi

# Run sync with exclusions
rclone bisync /root/flourisha flourisha: \
  --exclude "node_modules/" \
  --exclude "venv/" \
  --exclude ".venv/" \
  --exclude "**/node_modules/" \
  --exclude "**/venv/" \
  --resync \
  --interactive=false

# Report results
echo "✅ Flourisha synced to Google Drive"
```

### Example 2: Cron Job (Automated Daily)

**Script:** `/root/.claude/skills/flourisha-sync/sync-runner.sh`

```bash
#!/bin/bash

LOG_FILE="/var/log/flourisha-sync.log"
LOCK_FILE="/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck"

# Log start
echo "[$(date)] Starting flourisha-sync" >> "$LOG_FILE"

# Clean stale lock if needed
if [ -f "$LOCK_FILE" ]; then
  LOCK_AGE=$(($(date +%s) - $(stat -f%m "$LOCK_FILE" 2>/dev/null || stat -c%Y "$LOCK_FILE")))
  if [ "$LOCK_AGE" -gt 300 ]; then
    rclone deletefile "$LOCK_FILE" 2>&1 | tee -a "$LOG_FILE"
  fi
fi

# Run sync
rclone bisync /root/flourisha flourisha: \
  --exclude "node_modules/" \
  --exclude "venv/" \
  --exclude ".venv/" \
  --exclude "**/node_modules/" \
  --exclude "**/venv/" \
  --resync \
  --interactive=false \
  2>&1 | tee -a "$LOG_FILE"

# Log result
echo "[$(date)] Sync completed with exit code $?" >> "$LOG_FILE"
```

## Key Principles

1. **Automatic Exclusions**: Heavy directories are always excluded - no manual intervention needed
2. **Bidirectional**: Syncs both directions - local changes go to Drive, Drive changes come back
3. **Safe**: --resync mode handles conflicts intelligently
4. **Fast**: Excludes node_modules/venv = 90% fewer files to process
5. **Logged**: All syncs recorded for audit trail

## Integration Points

- **Local**: `/root/flourisha/` directory
- **Remote**: Google Drive via `flourisha:` rclone remote
- **Logs**: `/var/log/flourisha-sync.log`
- **Lock**: `/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck`
- **Cron**: Daily automated schedule

## Troubleshooting

**Sync is slow:**
- Check network connection
- Verify no other rclone operations running
- Consider running at off-peak hours

**Files not syncing:**
- Check if file is in exclusion list (node_modules, venv)
- Verify file is readable/writable locally
- Check Google Drive quota

**"Prior lock file found" error:**
- Previous sync was interrupted
- Run with `--force` to override OR manually delete lock file
- Check logs: `/var/log/flourisha-sync.log`

**Duplicate objects found:**
- Normal warning in --resync mode
- bisync handles automatically
- Usually indicates files already synced

## Output Format

When skill executes, return:

```
📋 SUMMARY: Synced Flourisha directory to Google Drive
🔍 ANALYSIS: Scanned 2,847 files, transferred 23 files, 0 errors
⚡ ACTIONS: Executed rclone bisync with node_modules/venv exclusions
✅ RESULTS: Sync completed successfully in 3m 42s
📊 STATUS: All systems synced - Google Drive is current
➡️ NEXT: Your files are safe in Google Drive, next auto-sync in 23h 15m
```
