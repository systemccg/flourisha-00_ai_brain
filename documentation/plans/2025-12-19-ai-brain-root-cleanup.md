# Plan: Clean Up 00_AI_Brain Root Files

## Overview

The `/root/flourisha/00_AI_Brain/` root directory contains 18 files that are a mix of:
- Active operational references (keep)
- Historical Phase 1 artifacts (archive or delete)
- Misplaced files (move to proper locations)
- Unnecessary files (delete)

---

## Understanding the ClickUp Autonomous Agent Architecture

**How prompts.py works:**

```
--project flourisha  →  set_active_project("flourisha")
                              ↓
                     load_prompt("initializer_prompt")
                              ↓
               Looks for: flourisha_initializer_prompt.md (FOUND)
                              ↓
                   Returns Flourisha-specific instructions
```

**The prompts folder has TWO sets:**

| Type | Files | Purpose |
|------|-------|---------|
| **Generic** | `initializer_prompt.md`, `coding_prompt.md`, `app_spec.xml` | For any new project (reads `app_spec.txt`) |
| **Flourisha** | `flourisha_initializer_prompt.md`, `flourisha_coding_prompt.md`, `flourisha_spec.txt` | For Flourisha project (reads SYSTEM_SPEC.md) |

**NOT redundant - they're a hierarchy:**
1. **Source of truth:** `SYSTEM_SPEC.md`, `AUTONOMOUS_TASK_SPEC.md` (documentation/)
2. **Agent instructions:** `flourisha_*_prompt.md` (tell agent WHERE to find source of truth)
3. **Quick summary:** `flourisha_spec.txt` (condensed reference so agent doesn't need full 1851-line spec)

**Recommendation for prompts folder:**
- KEEP generic prompts (for non-Flourisha projects)
- KEEP Flourisha prompts (they POINT TO source of truth, not duplicate it)
- DELETE `app_spec.xml` (22KB generic spec not used for Flourisha)

---

## Files Analysis Summary

### Files to MOVE to documentation/ (Per User Request)

| File | Destination | Reason |
|------|-------------|--------|
| `AUTONOMOUS_TASK_SPEC.md` | `documentation/AUTONOMOUS_TASK_SPEC.md` | User requested; keeps all docs together |

**After moving, update these references:**
- `documentation/SYSTEM_SPEC.md` - Update 3 references to point to new location
- `agents/clickup-autonomous/prompts/flourisha_coding_prompt.md` - Update path
- `agents/clickup-autonomous/prompts/flourisha_initializer_prompt.md` - Already correct!

### Files to KEEP in Root (Essential)

| File | Reason |
|------|--------|
| `QUICK_REFERENCE.md` | Referenced in SYSTEM_SPEC.md Quick Navigation |
| `README.md` | Entry point for directory, up-to-date |
| `.flourisha-config` | Active infrastructure config used by scripts |
| `.gitignore` | Standard, essential |
| `firebase.json` | Firebase config (expected location) |
| `.firebaserc` | Firebase project config |
| `requirements.txt` | Still used for dependencies |

### Files to MOVE to /root/ToBeDeleted (Historical/Obsolete)

| File | Reason |
|------|--------|
| `DEPLOYMENT_SUMMARY.txt` | Phase 1 historical report from 2025-12-06, no longer active |
| `INDEX.md` | Phase 1 file index, outdated, not referenced |
| `PHASE1_MIGRATION_STATUS.md` | Phase 1 complete, historical only |
| `PHASE1_VALIDATION_REPORT.md` | Phase 1 validation snapshot, historical only |
| `QUICK_DEPLOY.sh` | Phase 1 deployment script, not referenced |

### Files to MOVE to Proper Subdirectories

| File | Destination | Reason |
|------|-------------|--------|
| `SUPABASE_MIGRATION_GUIDE.md` | `documentation/database/` | Database documentation belongs there |
| `QUICK_REFERENCE_PROJECTS.md` | `documentation/guides/` | Guide documentation |
| `SKILLS_QUICK_REFERENCE.md` | `documentation/guides/` | Guide documentation |

### Files to DELETE (Unnecessary/Duplicate)

| File | Reason |
|------|--------|
| `test_gmail_integration.py` | Duplicate exists at `tests/test_gmail_integration.py` |
| `__init__.py` | Empty, unnecessary at root level |

### Agent Prompts Folder Cleanup

| File | Action | Reason |
|------|--------|--------|
| `app_spec.xml` | Move to ToBeDeleted | 22KB generic spec not used for Flourisha |
| `initializer_prompt.md` | KEEP | Generic template for non-Flourisha projects |
| `coding_prompt.md` | KEEP | Generic template for non-Flourisha projects |
| `flourisha_initializer_prompt.md` | KEEP | Flourisha-specific (points to SYSTEM_SPEC.md) |
| `flourisha_coding_prompt.md` | UPDATE | Update AUTONOMOUS_TASK_SPEC.md path |
| `flourisha_spec.txt` | KEEP | Condensed reference for agent |

## Execution Plan

### Step 1: Create /root/ToBeDeleted if not exists
```bash
mkdir -p /root/ToBeDeleted
```

### Step 2: Move AUTONOMOUS_TASK_SPEC.md to documentation/
```bash
mv /root/flourisha/00_AI_Brain/AUTONOMOUS_TASK_SPEC.md /root/flourisha/00_AI_Brain/documentation/
```

### Step 3: Update references to AUTONOMOUS_TASK_SPEC.md

**In SYSTEM_SPEC.md:** Update 3 references
- Line 1051: `../AUTONOMOUS_TASK_SPEC.md` → `AUTONOMOUS_TASK_SPEC.md`
- Line 1710: Update path reference
- Line 1825: Update in document hierarchy

**In flourisha_coding_prompt.md:** Update line 21
- `/root/flourisha/00_AI_Brain/AUTONOMOUS_TASK_SPEC.md` → `/root/flourisha/00_AI_Brain/documentation/AUTONOMOUS_TASK_SPEC.md`

### Step 4: Move historical Phase 1 files to ToBeDeleted
```bash
mv /root/flourisha/00_AI_Brain/DEPLOYMENT_SUMMARY.txt /root/ToBeDeleted/
mv /root/flourisha/00_AI_Brain/INDEX.md /root/ToBeDeleted/
mv /root/flourisha/00_AI_Brain/PHASE1_MIGRATION_STATUS.md /root/ToBeDeleted/
mv /root/flourisha/00_AI_Brain/PHASE1_VALIDATION_REPORT.md /root/ToBeDeleted/
mv /root/flourisha/00_AI_Brain/QUICK_DEPLOY.sh /root/ToBeDeleted/
```

### Step 5: Move app_spec.xml to ToBeDeleted
```bash
mv /root/flourisha/00_AI_Brain/agents/clickup-autonomous/prompts/app_spec.xml /root/ToBeDeleted/
```

### Step 6: Move files to proper subdirectories
```bash
mv /root/flourisha/00_AI_Brain/SUPABASE_MIGRATION_GUIDE.md /root/flourisha/00_AI_Brain/documentation/database/
mv /root/flourisha/00_AI_Brain/QUICK_REFERENCE_PROJECTS.md /root/flourisha/00_AI_Brain/documentation/guides/
mv /root/flourisha/00_AI_Brain/SKILLS_QUICK_REFERENCE.md /root/flourisha/00_AI_Brain/documentation/guides/
```

### Step 7: Delete unnecessary files
```bash
rm /root/flourisha/00_AI_Brain/test_gmail_integration.py
rm /root/flourisha/00_AI_Brain/__init__.py
```

### Step 8: Update DOCUMENTATION_MAP.md
Add entries for the newly moved files:
- `documentation/AUTONOMOUS_TASK_SPEC.md`
- `documentation/database/SUPABASE_MIGRATION_GUIDE.md`
- `documentation/guides/QUICK_REFERENCE_PROJECTS.md`
- `documentation/guides/SKILLS_QUICK_REFERENCE.md`

## After Cleanup - Expected Root Contents

```
/root/flourisha/00_AI_Brain/
├── QUICK_REFERENCE.md         # Quick commands reference (referenced in SYSTEM_SPEC)
├── README.md                  # Directory entry point
├── .flourisha-config          # Infrastructure config
├── .gitignore                 # Git ignore rules
├── firebase.json              # Firebase config
├── .firebaserc                # Firebase project
├── requirements.txt           # Python dependencies
└── [directories...]           # All subdirectories remain

/root/flourisha/00_AI_Brain/documentation/
├── SYSTEM_SPEC.md             # THE canonical reference
├── AUTONOMOUS_TASK_SPEC.md    # Task specifications (moved here)
├── FRONTEND_FEATURE_REGISTRY.md
├── DOCUMENTATION_MAP.md
├── database/
│   └── SUPABASE_MIGRATION_GUIDE.md  (moved here)
├── guides/
│   ├── QUICK_REFERENCE_PROJECTS.md  (moved here)
│   └── SKILLS_QUICK_REFERENCE.md    (moved here)
└── ...
```

## Verification Steps

1. Confirm tests/test_gmail_integration.py exists before deleting root copy
2. Verify SYSTEM_SPEC.md references are still valid after moves
3. Run `flourisha-sync` after cleanup to sync changes to Google Drive

## Files Summary

| Action | Count | Files |
|--------|-------|-------|
| Keep in root | 7 files | QUICK_REFERENCE.md, README.md, .flourisha-config, .gitignore, firebase.json, .firebaserc, requirements.txt |
| Move to documentation/ | 1 file | AUTONOMOUS_TASK_SPEC.md |
| Move to documentation/database/ | 1 file | SUPABASE_MIGRATION_GUIDE.md |
| Move to documentation/guides/ | 2 files | QUICK_REFERENCE_PROJECTS.md, SKILLS_QUICK_REFERENCE.md |
| Move to ToBeDeleted | 6 files | DEPLOYMENT_SUMMARY.txt, INDEX.md, PHASE1_MIGRATION_STATUS.md, PHASE1_VALIDATION_REPORT.md, QUICK_DEPLOY.sh, app_spec.xml |
| Delete | 2 files | test_gmail_integration.py, __init__.py |
| **Total Root Files** | **18 files** | |

## Key Insight: Agent Architecture

The clickup-autonomous agent is NOT redundant with SYSTEM_SPEC.md:

```
Source of Truth (documentation/)
         ↓
SYSTEM_SPEC.md ← AUTONOMOUS_TASK_SPEC.md
         ↓
    [Referenced by]
         ↓
Agent Instructions (prompts/)
         ↓
flourisha_*_prompt.md → Tell agent to READ source of truth
         ↓
flourisha_spec.txt → Quick summary (80 lines vs 1851 lines)
```

The prompts are INSTRUCTIONS, not duplicates. They tell the agent WHERE to find the canonical documentation.
