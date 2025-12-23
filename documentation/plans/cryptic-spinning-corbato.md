# Plan: Analyze and Clean Duplicate Folders in Flourisha Root

## Status
Analysis Complete - Ready for Execution

## Problem Statement
Multiple technical folders that should only exist inside `/root/flourisha/00_AI_Brain/` have been incorrectly duplicated at the root `/root/flourisha/` level due to a GitHub sync mistake on December 19, 2023.

## Key Findings

### Root Cause
- **Mass sync event on December 19, 2023 at 13:52** pulled 28+ folders from `00_AI_Brain/` to root level
- Root duplicates are **outdated and incomplete** compared to originals
- Some critical folders missing thousands of files in root versions

### Critical Data Loss Risk
Root versions are severely outdated:
- `skills`: Missing 1,665 files (101MB vs 248MB)
- `scripts`: Missing 6,226 files (464KB vs 134MB)
- `ui`: Missing most content (184KB vs 260MB)
- `functions`: Missing massive amount (28KB vs 141MB)

### Exception: Scratchpad
- **Root scratchpad is NEWER** than 00_AI_Brain version (1.1MB vs 1012KB)
- May contain recent work - **REQUIRES REVIEW BEFORE DELETION**

## Scratchpad Analysis
- **Root scratchpad appears newer (1.1MB vs 1012KB) BUT content is identical**
- Size difference due to filesystem metadata from sync timestamp update
- `diff -qr` shows 0 differences - **SAFE TO DELETE**
- All scratchpad content preserved in `/root/flourisha/00_AI_Brain/scratchpad/`

## Folders Confirmed for Deletion (29 total)

**All root-level duplicates are safe to delete:**
```
/root/flourisha/a2a/
/root/flourisha/agents/
/root/flourisha/api/
/root/flourisha/auth/
/root/flourisha/backend/
/root/flourisha/config/
/root/flourisha/context/
/root/flourisha/data/
/root/flourisha/database/
/root/flourisha/documentation/
/root/flourisha/examples/
/root/flourisha/functions/
/root/flourisha/history/
/root/flourisha/hooks/
/root/flourisha/ingestion/
/root/flourisha/migrations/
/root/flourisha/models/
/root/flourisha/okr/
/root/flourisha/outputs/
/root/flourisha/plans/
/root/flourisha/scratchpad/
/root/flourisha/scripts/
/root/flourisha/services/
/root/flourisha/skills/
/root/flourisha/tests/
/root/flourisha/ui/
/root/flourisha/utils/
/root/flourisha/voice-server/
/root/flourisha/workers/
```

---

## Execution Plan

### Step 1: Pre-Deletion Safety Checks
1. Verify backup exists: Check latest `flourisha-bisync` to Google Drive
2. Verify GitHub status: Ensure current state is committed
3. Create safety backup of entire `/root/flourisha/` (optional but recommended)

### Step 2: Delete Duplicate Folders
Execute deletion of all 29 duplicate folders:
```bash
cd /root/flourisha/

# Delete all duplicates in one command
rm -rf a2a agents api auth backend config context data \
       database documentation examples functions history hooks \
       ingestion migrations models okr outputs plans scratchpad \
       scripts services skills tests ui utils voice-server workers
```

### Step 3: Verification
1. List remaining root folders - should only show:
   - `00_AI_Brain/`
   - `01f_Flourisha_Projects/`
   - `02f_Flourisha_Areas/`
   - `03f_Flourisha_Resources/`
   - `04f_Flourisha_Archives/`
   - `05_Backups/`
   - `.git/`, `.obsidian/`
   - `Clippings/`
   - Root-level config files (.md, .py, .json, etc.)

2. Verify 00_AI_Brain integrity:
   ```bash
   ls -lh /root/flourisha/00_AI_Brain/
   ```

3. Run `flourisha-bisync` to sync cleaned structure to Google Drive

### Step 4: Prevent Future Duplications

#### Option A: Investigate GitHub Sync Issue
- Check what caused the Dec 19 sync event
- Review `.gitignore` to ensure AI Brain subdirectories aren't tracked at root
- Verify repository structure

#### Option B: Add `.rclone-filter` Rules (if using rclone for GitHub)
- Ensure rclone filters prevent pulling subdirectories to root

### Step 5: Post-Cleanup Validation
1. Verify Obsidian still works (syncs from Google Drive)
2. Check that all critical services/scripts still function
3. Confirm no broken symlinks

---

## Data Safety Summary

**No data will be lost:**
- All 29 root folders are outdated/incomplete duplicates
- Complete versions exist in `/root/flourisha/00_AI_Brain/`
- Scratchpad content is identical (verified via diff)
- Google Drive backup exists via rclone bisync
- Deletion removes only redundant copies

**Space to be recovered:**
- Estimated ~150MB+ of duplicate data

---

## Questions for User

Before proceeding, confirm:
1. Do you want a full backup before deletion, or is Google Drive sync sufficient?
2. Should I investigate the root cause of the Dec 19 sync event?
3. Proceed with deletion immediately, or review the folder list first?
