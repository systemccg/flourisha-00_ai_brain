# Google Drive Sync Recovery & Safety Guide

**Date:** 2025-11-19
**Status:** 🚨 CRITICAL - Sync Script Fixed After Data Loss Incident

---

## 🚨 What Happened

On 2025-11-19, the flourisha-push script accidentally **deleted two folders from Google Drive**:
- `03f_Flourisha_Resources/`
- `04f_Flourisha_Archives/`

**Root Cause:** The script used `rclone sync` which is DESTRUCTIVE - it makes the destination match the source exactly, deleting anything not in source.

**Impact:** These folders existed on Google Drive but not locally, so the sync deleted them from Google Drive.

---

## ✅ Recovery Status: COMPLETE

### Folders Successfully Restored! ✅

Both deleted folders have been restored from Google Drive Trash and synced locally:

**Verified restoration:**
```bash
rclone lsf flourisha: --dirs-only
# Shows both folders present:
# 03f_Flourisha_Resources/
# 04f_Flourisha_Archives/

ls -la /root/flourisha/ | grep -E "Resources|Archives"
# drwxr-xr-x  2 root root 4096 Nov 17 00:33 03f_Flourisha_Resources
# drwxr-xr-x  2 root root 4096 Nov 17 00:33 04f_Flourisha_Archives
```

**Bisync Initialized:** 2025-11-19 23:47:29

### How to Restore (Manual)

**Option 1: Via Google Drive Web Interface (Recommended)**
1. Go to https://drive.google.com
2. Navigate to the "Flourisha_gDrive" shared drive
3. Click "Trash" in the left sidebar
4. Find `03f_Flourisha_Resources` and `04f_Flourisha_Archives`
5. Right-click each → "Restore"
6. Verify they're back in the main drive

**Option 2: Via rclone cleanup command**
```bash
# Note: rclone doesn't have native restore from trash for shared drives
# Use the web interface instead
```

**After Restoration:**
```bash
# Sync them back to local
flourisha-pull

# Verify they're present locally
ls -la /root/flourisha/
```

---

## 🛡️ What Was Fixed

### 1. Changed Push Script from SYNC to COPY

**Before (DESTRUCTIVE):**
```bash
rclone sync "$FLOURISHA_LOCAL" "$FLOURISHA_REMOTE" \
    --backup-dir="$BACKUP_DIR_REMOTE" \
    ...
```
- ❌ Deletes files on Google Drive that don't exist locally
- ❌ Can cause permanent data loss
- ❌ Unsafe for bidirectional workflows

**After (SAFE):**
```bash
rclone copy "$FLOURISHA_LOCAL" "$FLOURISHA_REMOTE" \
    --update \
    ...
```
- ✅ Only uploads new/changed files
- ✅ NEVER deletes files from Google Drive
- ✅ Safe for bidirectional workflows
- ✅ Clear messaging about safety

### 2. Improved Messaging

**Before:**
```
Skipping X - file only exists locally (will be uploaded)
```
- Confusing: "Skipping" suggests it won't upload

**After:**
```
✓ New file to upload: X
```
- Clear: File will be uploaded

**Added Safety Notices:**
```
⬆️  Uploading changes from local to Google Drive...
  (Using safe copy mode - will NOT delete files from Google Drive)

✅ Upload completed successfully
  All local changes have been uploaded to Google Drive
  Note: Files on Google Drive that don't exist locally were NOT deleted

💡 Note: This script uses SAFE COPY mode - it will never delete files from Google Drive
```

### 3. Pull Script Unchanged (Intentional)

The `flourisha-pull` script still uses `rclone sync` because:
- User controls local filesystem
- Deleted files go to `ToBeDeleted/` (30-day retention)
- Safe to let Google Drive be the source of truth

---

## 📋 Safe Sync Practices Going Forward

### Bidirectional Sync (Recommended)

```bash
# Always dry-run first for major changes
flourisha-sync --dry-run

# Review output carefully
# If looks good, do actual sync
flourisha-sync

# Behavior:
# - New files on either side → synced to other
# - Deletions on either side → synced to other
# - Modified files → newer version wins
# - Conflicts → both versions kept
# - Deleted files backed up to ToBeDeleted/ (30 days)
```

### Test Mode (00_SYNC_TEST folder only)

```bash
# Test in isolated folder
flourisha-sync --test --dry-run

# Safe testing without affecting main data
flourisha-sync --test
```

**See Full Guide:** `/root/flourisha/00_AI_Brain/SYNC_GUIDE.md`

---

## 🔍 How to Check What's on Google Drive

### List All Folders
```bash
rclone lsf flourisha: --dirs-only
```

### Check Specific Folder
```bash
rclone lsf "flourisha:03f_Flourisha_Resources/" -R | head -20
```

### Check Trash
```bash
rclone lsf flourisha: --drive-trashed-only
```

### Compare Local vs Remote
```bash
# Check differences
rclone check /root/flourisha flourisha: \
    --exclude ".obsidian/**" \
    --exclude "ToBeDeleted/**" \
    --one-way
```

---

## 📊 Current Sync Configuration

### Filter File: `/root/flourisha/.rclone-filter`

Automatically excludes from sync:
- `node_modules/` (all locations)
- `__pycache__/`, `*.pyc`, `.venv/`, `venv/`
- `.git/` repositories
- `dist/`, `build/`, `.next/`, `.nuxt/`, `.vite/`
- `.vscode/`, `.idea/`, `*.swp`
- `*.db`, `*.sqlite`, `*.sqlite3`
- Large GIF files (`**/*-logo*.gif`)
- `**/fabric-repo/`
- Temp files (`*.tmp`, `*.log`, `.cache/`)

### Always Excluded (in scripts)

- `.obsidian/**` - Obsidian workspace (local only)
- `ToBeDeleted/**` - Backup directory
- `**/*.CONFLICT-*` - Conflict resolution files
- `.DS_Store` - macOS metadata

---

## 🚀 Verification Checklist

After restoring the deleted folders, verify:

- [ ] `03f_Flourisha_Resources/` restored on Google Drive
- [ ] `04f_Flourisha_Archives/` restored on Google Drive
- [ ] Run `flourisha-pull --dry-run` to see what will download
- [ ] Run `flourisha-pull` to sync locally
- [ ] Verify both folders exist at `/root/flourisha/`
- [ ] Run `flourisha-push --dry-run` to verify no deletions will occur
- [ ] Confirm messaging is clear and accurate
- [ ] Test with `00_SYNC_TEST` folder to ensure safety

---

## 📝 Technical Details

### What `rclone sync` Does
- Makes destination EXACTLY match source
- Deletes files on destination not in source
- Overwrites different files
- Good for: Making perfect mirror copies
- Bad for: Bidirectional workflows where both sides can have unique files

### What `rclone copy` Does
- Copies files from source to destination
- NEVER deletes files on destination
- Only uploads new/changed files
- Good for: Uploading changes without affecting destination-only files
- Bad for: When you actually want to delete remote files

### What `rclone bisync` Does (experimental)
- True bidirectional sync
- Tracks changes on both sides
- Resolves conflicts
- Currently experimental/beta
- Requires initial sync setup

---

## 🎯 Summary

**Problem:** Used destructive `rclone sync` which deleted Google Drive folders
**Status:** Folders are in Google Drive Trash (recoverable for 30 days)
**Solution:** Changed to safe `rclone copy` mode with clear messaging
**Action Required:** Restore folders via Google Drive web interface

---

**Last Updated:** 2025-11-19
**Maintainer:** Flourisha AI Brain
**Priority:** 🚨 HIGH - Restore deleted folders immediately
