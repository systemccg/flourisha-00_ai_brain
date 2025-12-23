# Server Migration - Ready to Execute

**Status**: ✅ All scripts and documentation prepared  
**Date**: 2025-11-10

---

## What's Been Created

### 1. Complete Documentation
- **`/root/SERVER_MIGRATION_PLAN.md`** - Comprehensive migration guide with all details
- **`/root/local-ai-packaged/MIGRATION_QUICK_START.md`** - Fast-track guide (3 commands!)
- This summary file

### 2. Automated Scripts
- **`/root/local-ai-packaged/scripts/export_for_migration.sh`** - One-command export
- **`/root/local-ai-packaged/scripts/restore_from_migration.sh`** - One-command restore

### 3. Safety Features
- Updated `.gitignore` to prevent committing secrets
- Checksum verification for data integrity
- Volume backups as safety net
- Old server stays intact (can retry)

---

## Quick Start (3 Commands)

### On Current Server:
```bash
cd /root/local-ai-packaged
./scripts/export_for_migration.sh
```

### Transfer Files:
```bash
scp -r /root/migration_* user@new-server:/root/
scp /root/secrets_*.tar.gz user@new-server:/root/
```

### On New Server:
```bash
cd /root/local-ai-packaged
./scripts/restore_from_migration.sh /root/migration_*
```

**Total Time**: 1-2 hours

---

## What Gets Migrated

### ✅ Configuration Files
- docker-compose.yml
- .env files (via encrypted archive)
- Caddyfile
- All scripts
- Documentation

### ✅ n8n Data
- All workflows (including your fixed Multi-Tenant RAG workflow)
- SQLite database
- Credentials (encrypted)
- Execution history

### ✅ Databases
- Supabase PostgreSQL (all tenants, users, auth)
- Langfuse PostgreSQL
- Neo4j graph database
- n8n SQLite

### ✅ Application Data
- Qdrant vector embeddings
- Langfuse metrics (ClickHouse, MinIO)
- All Docker volumes

---

## GitHub Strategy

Your repo is already connected to: `https://github.com/coleam00/local-ai-packaged.git`

**What to commit:**
- ✅ Scripts (export, restore)
- ✅ Documentation (MIGRATION_*.md, CLAUDE.md)
- ✅ Configs (docker-compose.yml, Caddyfile)
- ✅ n8n workflow backups (JSONs)
- ✅ .env.example (template)

**NEVER commit:**
- ❌ .env (actual secrets)
- ❌ Database dumps
- ❌ secrets_*.tar.gz
- ❌ Docker volumes

The `.gitignore` file has been updated to protect you from accidentally committing secrets.

---

## Recommended Workflow

### Option 1: Simple Migration (No GitHub)
1. Run export script
2. Transfer files directly via scp
3. Run restore script
4. Done!

### Option 2: Migration + GitHub Backup (Recommended)
1. Run export script
2. Commit configs to GitHub (no secrets!)
3. Transfer data files via scp
4. On new server: clone GitHub repo
5. Transfer secrets separately
6. Run restore script

---

## Before You Start

### Pre-Flight Checklist
- [ ] New server is accessible (SSH, IP address)
- [ ] New server has enough disk space (>10GB recommended)
- [ ] You have backup transfer method ready (scp, cloud, USB)
- [ ] Current server is healthy (all containers running)
- [ ] You've read MIGRATION_QUICK_START.md

### Test the Export (Optional)
```bash
# Dry run to see what will be exported
cd /root/local-ai-packaged
./scripts/export_for_migration.sh /tmp/test_migration
du -sh /tmp/test_migration/*
rm -rf /tmp/test_migration
```

---

## Current System Stats

**Services Running:**
- Supabase (PostgreSQL, Auth, Storage, Studio)
- n8n (with 2 active workflows including Multi-Tenant RAG)
- Neo4j
- Langfuse
- Qdrant
- Coolify

**Total Size to Transfer:** ~3-5 GB (estimated)

**Docker Volumes:** 39 volumes (only critical ones will be backed up)

---

## Safety Features

1. **Non-Destructive**: Old server stays untouched
2. **Checksums**: Verify file integrity after transfer
3. **Multiple Backups**: SQL dumps + volume backups
4. **Retry-Friendly**: Can run export/restore multiple times
5. **Verification**: Scripts check if restoration worked

---

## Next Steps

**Choose your approach:**

### A. Quick Migration (fastest)
```bash
# Read the quick start guide
cat /root/local-ai-packaged/MIGRATION_QUICK_START.md

# Run when ready
cd /root/local-ai-packaged
./scripts/export_for_migration.sh
```

### B. Detailed Planning (safest)
```bash
# Read the comprehensive plan
cat /root/SERVER_MIGRATION_PLAN.md

# Test export first (optional)
./scripts/export_for_migration.sh /tmp/test_export
```

### C. GitHub First (best for long-term)
```bash
# Review what will be committed
cd /root/local-ai-packaged
git status

# Commit configs (no secrets!)
git add scripts/ MIGRATION_*.md CLAUDE.md
git commit -m "Migration scripts and documentation"
git push

# Then run export
./scripts/export_for_migration.sh
```

---

## Questions to Consider

1. **Do you have access to the new server?**
   - If yes → Start with export script
   - If no → Get access first

2. **Can servers connect directly?**
   - If yes → Use scp for transfer
   - If no → Use cloud storage or USB

3. **Want GitHub backup?**
   - If yes → Commit configs first
   - If no → Just run export/restore

4. **Need to test first?**
   - If yes → Run export to /tmp/ and review
   - If no → Run full export when ready

---

## Support

All scripts include:
- Progress logging
- Error handling
- Verification checks
- Helpful output messages

If something fails:
- Old server still has everything
- Can retry migration
- Can restore from backups
- Logs show what went wrong

---

## Summary

✅ **Everything is ready!**

You have:
- Complete documentation (detailed + quick start)
- Automated scripts (export + restore)
- Protected secrets (.gitignore updated)
- Existing GitHub repo to use

**When you're ready, just run:**
```bash
cd /root/local-ai-packaged
./scripts/export_for_migration.sh
```

The script will do everything automatically and tell you exactly what to do next.

---

**Good luck with your migration!** 🚀
