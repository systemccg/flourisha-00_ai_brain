# /root Directory Backup Coverage

**Last Updated:** 2025-11-20

## Overview

This document tracks what gets backed up from `/root` and how to restore it in a disaster recovery scenario.

---

## What IS Backed Up

### ✅ Tier 1: CRITICAL - Multiple Backups

| Location | Backup Method | Frequency | Restore Priority |
|----------|---------------|-----------|------------------|
| **Docker volumes** | Automated backup script | Daily (Tier 1), Weekly (Tier 2) | **CRITICAL** |
| **Server configs** | Git repo `server-config-backup` | Daily + on changes | **CRITICAL** |
| **.claude/** | Should be in personal backup | Manual | **CRITICAL** |

#### Docker Volumes (Automated)
- Location: `/var/lib/docker/volumes/`
- Backup: `/root/backups/backup-daily-*.tar.gz`
- Includes: WordPress, Coolify, Portainer, n8n workflows
- Synced to: Google Drive `flourisha:/05_Backups/server-backups/`

#### Server Configurations (Git)
- Location: `/root/server-config-backup/`
- Backup: Git repo at `git@github.com:systemccg/server-config-backup.git`
- Includes:
  - All `.env` files
  - Modified `docker-compose.yml` files
  - Custom scripts
  - Traefik configs
  - n8n workflow backups (`/root/n8n-*.json`)

### ✅ Tier 2: IMPORTANT - Version Controlled

| Location | Backup Method | Frequency |
|----------|---------------|-----------|
| **Flourisha scripts** | Google Drive sync | On changes |
| **Flourisha AI Brain** | Google Drive sync | On changes |

#### Flourisha Directory
- Location: `/root/flourisha/`
- Synced to: Google Drive `Flourisha_gDrive`
- Command: `flourisha-bisync`
- Includes:
  - All backup scripts (`00_AI_Brain/scripts/backups/`)
  - Security scripts (`00_AI_Brain/scripts/security/`)
  - Infrastructure scripts (`00_AI_Brain/scripts/infrastructure/`)
  - Documentation
  - PARA-organized projects and resources

---

## What IS NOT Backed Up (But Should Be Considered)

### ⚠️ Gaps in Coverage

| Location | Size | Risk | Recommendation |
|----------|------|------|----------------|
| `/root/.ssh/` | <1MB | **HIGH** | Add to config backup |
| `/root/.claude.json` | 43KB | **HIGH** | Back up manually |
| `/root/test-*.sh` | <1MB | MEDIUM | Document or delete |
| `/root/n8n-*.json` | 400KB | **HIGH** | Already in config backup ✓ |
| `/root/scripts/` | <1MB | MEDIUM | Now in Flourisha ✓ |

### Specific Files Needing Attention

```bash
# Critical files in /root (not currently backed up):
/root/.ssh/                           # SSH keys - CRITICAL
/root/.claude.json                    # Claude Code config
/root/.bashrc_flourisha               # Bash customizations
/root/test-full-integration.sh        # Integration tests
/root/test-google-drive.sh            # Testing scripts
/root/test-odoo-connection.sh         # Testing scripts
/root/get-google-refresh-token.sh     # Auth helper
/root/setup_gdrive_quick.sh           # Setup helper
```

---

## What Should NOT Be Backed Up

### ❌ Excluded (Recreatable or Transient)

| Location | Size | Reason |
|----------|------|--------|
| `/root/.cache/` | Variable | Cache data |
| `/root/.bun/` | Small | Bun runtime (reinstallable) |
| `/root/.nvm/` | Small | Node version manager |
| `/root/.npm/` | Small | npm cache |
| `/root/.docker/` | Small | Docker CLI config |
| `/root/local-ai-packaged/` | 2.7GB | **Upstream git repo** |
| `/root/mcp/` | 849MB | **Upstream git repo** |
| `/root/pai/` | 147MB | **Upstream git repo** |
| `/root/graphiti/` | 33MB | **Upstream git repo** |
| `/root/erpnext/` | 12MB | **Upstream git repo** |
| `/root/monitoring/` | 80KB | Docker compose (in config backup) |
| `/root/wordpress/` | Small | Docker compose (in config backup) |
| `/root/traefik/` | 172KB | **In config backup** |
| `/root/filebrowser/` | Small | Docker compose (in config backup) |
| `/root/portainer/` | Small | Docker compose (in config backup) |
| `/root/ToBeDeleted/` | 56KB | Temporary |
| `/root/aidocs/` | 788KB | Temporary/recreatable |
| `/root/backups/old_system_archive/` | 12GB | **DELETE AFTER TESTING** |

---

## Backup Coverage Summary

### By Category

**CRITICAL DATA (Multi-redundant):**
- ✅ Docker volumes → Daily backup + Google Drive
- ✅ Server configs → Git + daily commit
- ⚠️ SSH keys → **NOT BACKED UP**
- ⚠️ Claude config → **NOT BACKED UP**

**IMPORTANT DATA (Single backup):**
- ✅ Flourisha scripts → Google Drive sync
- ✅ Custom scripts → Now in Flourisha
- ✅ n8n backups → Git repo

**UPSTREAM REPOS (Not backed up):**
- ❌ local-ai-packaged (2.7GB) → Git clone on restore
- ❌ mcp (849MB) → Git clone on restore
- ❌ pai (147MB) → Git clone on restore
- ❌ All other git repos → Git clone on restore

---

## Disaster Recovery Procedure

### 1. Fresh Server Setup

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install -y docker-compose-plugin

# Install rclone for Google Drive
apt install -y rclone
```

### 2. Restore Upstream Repositories

```bash
# Clone main infrastructure
cd /root
git clone -b stable https://github.com/coleam00/local-ai-packaged.git
git clone https://github.com/your-mcp-repo/mcp.git
git clone https://github.com/your-pai-repo/pai.git

# Clone other services as needed
```

### 3. Restore Configurations

```bash
# Clone private config backup
cd /root
git clone git@github.com:systemccg/server-config-backup.git

# Run restoration script
cd /root/server-config-backup
./restore_configs.sh
```

### 4. Restore Flourisha

```bash
# Configure rclone (interactive)
rclone config

# Sync Flourisha from Google Drive
rclone sync flourisha:/ /root/flourisha
```

### 5. Restore Docker Volumes

```bash
# Download latest backup from Google Drive
rclone copy flourisha:/05_Backups/server-backups/backup-latest.tar.gz /root/backups/

# Extract and restore
cd /root
/root/backups/restore_volumes.sh
```

### 6. Manually Restore Critical Files

```bash
# SSH keys (from personal backup)
cp -r ~/backup/.ssh /root/

# Claude config (from personal backup)
cp ~/backup/.claude.json /root/

# Set permissions
chmod 600 /root/.ssh/id_*
chmod 700 /root/.ssh
```

### 7. Start Services

```bash
# Start in order
cd /root/local-ai-packaged
docker-compose up -d

# Verify
docker ps
```

---

## Recommendations

### Immediate Actions

1. **Add SSH key backup to config script:**
   ```bash
   # Edit /root/flourisha/00_AI_Brain/scripts/backups/backup_configs.sh
   # Add:
   mkdir -p "$BACKUP_DIR/ssh"
   cp -r /root/.ssh/* "$BACKUP_DIR/ssh/" 2>/dev/null || true
   ```

2. **Back up .claude.json:**
   ```bash
   # Add to config backup script
   cp /root/.claude.json "$BACKUP_DIR/configs/" 2>/dev/null || true
   ```

3. **Clean up testing scripts:**
   ```bash
   # Move to Flourisha or delete
   mv /root/test-*.sh /root/flourisha/00_AI_Brain/scripts/testing/ || rm /root/test-*.sh
   ```

4. **Delete old backup archive:**
   ```bash
   # After confirming new system works
   rm -rf /root/backups/old_system_archive/  # Frees 12GB
   ```

### Regular Maintenance

1. **Weekly:** Review `/root` for new files
   ```bash
   find /root -maxdepth 1 -type f -mtime -7
   ```

2. **Monthly:** Verify backups are working
   ```bash
   /root/flourisha/00_AI_Brain/scripts/backups/verify_backups.sh
   ```

3. **Quarterly:** Test disaster recovery procedure

---

## Backup Storage Locations

### Local
- `/root/backups/backup-daily-*.tar.gz` - Docker volumes (47MB daily)
- `/root/backups/backup-weekly-*.tar.gz` - Docker volumes + configs (~100MB weekly)
- `/root/backups/backup-latest.tar.gz` - Symlink to latest

### Google Drive
- `flourisha:/05_Backups/server-backups/` - All backup archives
- `flourisha:/` - Full Flourisha sync (scripts, docs, projects)

### Git
- `git@github.com:systemccg/server-config-backup.git` - Server configurations

### Personal Backup (Manual)
- SSH keys
- Claude config
- Any other sensitive credentials

---

## Total Backup Size

| Backup Type | Size | Frequency | Location |
|-------------|------|-----------|----------|
| Daily volumes | 47MB | Daily | Local + GDrive |
| Weekly volumes | ~100MB | Weekly | Local + GDrive |
| Server configs | 2.7MB | Daily | Git |
| Flourisha | 8.9MB | On changes | GDrive |
| **Total per week** | **~400MB** | - | Multiple |

---

## Questions to Answer

- [ ] Should `.ssh/` be added to automated backup?
- [ ] Should `.claude.json` be added to automated backup?
- [ ] Are testing scripts in `/root` still needed?
- [ ] Should PAI directory (147MB) be backed up or just re-cloned?
- [ ] When can we delete `/root/backups/old_system_archive/`?

---

**Last Review:** 2025-11-20
**Next Review:** 2025-12-01
