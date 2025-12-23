#!/bin/bash
#
# Configuration Backup Script
# Backs up all custom configurations (NOT upstream repo content)
# Creates a Git-ready directory structure for version control
#

set -e

BACKUP_DIR="/root/backups/server-config-backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="/var/log/config_backup.log"

echo "=== Configuration Backup Started: $(date) ===" | tee -a "$BACKUP_LOG"

# Create backup directory structure
mkdir -p "$BACKUP_DIR"/{docker-compose,scripts,configs,env-files}

echo "Backing up .env files..." | tee -a "$BACKUP_LOG"
# Backup all .env files (these contain your secrets and customizations)
find /root -maxdepth 3 -name ".env" -type f 2>/dev/null | while read envfile; do
    relative_path=$(echo "$envfile" | sed 's|/root/||')
    target_dir="$BACKUP_DIR/env-files/$(dirname "$relative_path")"
    mkdir -p "$target_dir"
    cp "$envfile" "$target_dir/"
    echo "  ✓ $envfile" | tee -a "$BACKUP_LOG"
done

echo "Backing up docker-compose files..." | tee -a "$BACKUP_LOG"
# Backup docker-compose files
cp /root/wordpress/docker-compose.yml "$BACKUP_DIR/docker-compose/wordpress.yml" 2>/dev/null || true
cp /root/traefik/docker-compose.yml "$BACKUP_DIR/docker-compose/traefik.yml" 2>/dev/null || true
cp /root/filebrowser/docker-compose.yml "$BACKUP_DIR/docker-compose/filebrowser.yml" 2>/dev/null || true
cp /root/portainer/docker-compose.yml "$BACKUP_DIR/docker-compose/portainer.yml" 2>/dev/null || true
cp /root/monitoring/docker-compose.yml "$BACKUP_DIR/docker-compose/monitoring.yml" 2>/dev/null || true
cp /root/graphiti/docker-compose.yml "$BACKUP_DIR/docker-compose/graphiti.yml" 2>/dev/null || true

# Only backup local-ai-packaged docker-compose if you've modified it
# (Compare with upstream to see if modified)
if [ -f /root/local-ai-packaged/docker-compose.yml ]; then
    cp /root/local-ai-packaged/docker-compose.yml "$BACKUP_DIR/docker-compose/local-ai-packaged.yml"
fi

echo "Backing up custom scripts..." | tee -a "$BACKUP_LOG"
# Backup custom scripts
if [ -d /root/scripts ]; then
    cp -r /root/scripts/* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi

echo "Backing up service configurations..." | tee -a "$BACKUP_LOG"
# Backup Traefik configuration files
if [ -d /root/traefik ]; then
    mkdir -p "$BACKUP_DIR/configs/traefik"
    cp -r /root/traefik/* "$BACKUP_DIR/configs/traefik/" 2>/dev/null || true
    # Remove docker-compose.yml since we already copied it
    rm -f "$BACKUP_DIR/configs/traefik/docker-compose.yml"
fi

# Backup n8n credentials and workflows (if backup files exist)
if [ -f /root/n8n-credentials-backup.json ]; then
    mkdir -p "$BACKUP_DIR/configs/n8n"
    cp /root/n8n-credentials-backup.json "$BACKUP_DIR/configs/n8n/"
fi
if [ -f /root/n8n-workflows-backup.json ]; then
    mkdir -p "$BACKUP_DIR/configs/n8n"
    cp /root/n8n-workflows-backup.json "$BACKUP_DIR/configs/n8n/"
fi

# Backup local-ai-packaged customizations (scripts, custom configs)
if [ -d /root/local-ai-packaged/n8n/scripts ]; then
    mkdir -p "$BACKUP_DIR/configs/local-ai-packaged/n8n"
    cp -r /root/local-ai-packaged/n8n/scripts "$BACKUP_DIR/configs/local-ai-packaged/n8n/"
fi

# Backup any custom workflow files
if [ -d /root/local-ai-packaged/n8n/backup/workflows ]; then
    mkdir -p "$BACKUP_DIR/configs/local-ai-packaged/n8n"
    cp -r /root/local-ai-packaged/n8n/backup/workflows "$BACKUP_DIR/configs/local-ai-packaged/n8n/" 2>/dev/null || true
fi

echo "Creating restoration script..." | tee -a "$BACKUP_LOG"
# Create a restoration script
cat > "$BACKUP_DIR/restore_configs.sh" << 'RESTORE_SCRIPT'
#!/bin/bash
#
# Configuration Restoration Script
# Run this on a new server after cloning upstream repos
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Restoring configurations from $SCRIPT_DIR ==="

# Restore .env files
echo "Restoring .env files..."
if [ -d "$SCRIPT_DIR/env-files" ]; then
    cd "$SCRIPT_DIR/env-files"
    find . -name ".env" -type f | while read envfile; do
        target_path="/root/${envfile#./}"
        target_dir=$(dirname "$target_path")
        mkdir -p "$target_dir"
        cp "$envfile" "$target_path"
        echo "  ✓ Restored $target_path"
    done
fi

# Restore docker-compose files
echo "Restoring docker-compose files..."
cp "$SCRIPT_DIR/docker-compose/wordpress.yml" /root/wordpress/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/traefik.yml" /root/traefik/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/filebrowser.yml" /root/filebrowser/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/portainer.yml" /root/portainer/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/monitoring.yml" /root/monitoring/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/graphiti.yml" /root/graphiti/docker-compose.yml 2>/dev/null || true
cp "$SCRIPT_DIR/docker-compose/local-ai-packaged.yml" /root/local-ai-packaged/docker-compose.yml 2>/dev/null || true

# Restore scripts
echo "Restoring scripts..."
if [ -d "$SCRIPT_DIR/scripts" ]; then
    mkdir -p /root/scripts
    cp -r "$SCRIPT_DIR/scripts/"* /root/scripts/
    chmod +x /root/scripts/*.sh 2>/dev/null || true
fi

# Restore Traefik configs
if [ -d "$SCRIPT_DIR/configs/traefik" ]; then
    mkdir -p /root/traefik
    cp -r "$SCRIPT_DIR/configs/traefik/"* /root/traefik/
fi

# Restore n8n backups
if [ -d "$SCRIPT_DIR/configs/n8n" ]; then
    cp "$SCRIPT_DIR/configs/n8n/"*.json /root/ 2>/dev/null || true
fi

# Restore local-ai-packaged customizations
if [ -d "$SCRIPT_DIR/configs/local-ai-packaged" ]; then
    cp -r "$SCRIPT_DIR/configs/local-ai-packaged/"* /root/local-ai-packaged/ 2>/dev/null || true
fi

echo "=== Configuration restoration complete ==="
echo "Next steps:"
echo "1. Review restored files"
echo "2. Restore Docker volumes using restore_volumes.sh"
echo "3. Start services in order: Traefik -> WordPress -> Local AI stack"
RESTORE_SCRIPT

chmod +x "$BACKUP_DIR/restore_configs.sh"

echo "Creating README..." | tee -a "$BACKUP_LOG"
# Create README
cat > "$BACKUP_DIR/README.md" << 'README'
# Server Configuration Backup

This directory contains all custom configurations for the server.
It does NOT contain upstream repository code (which can be re-cloned).

## What's Backed Up

- `.env` files (all secrets and configuration)
- Modified `docker-compose.yml` files
- Custom scripts
- Service configurations (Traefik, n8n, etc.)
- Workflow backups

## How to Use

### On This Server (Backup)

Run the backup script regularly:
```bash
/root/backups/backup_configs.sh
```

Commit changes to your private Git repo:
```bash
cd /root/server-config-backup
git add .
git commit -m "Config backup $(date +%Y-%m-%d)"
git push
```

### On New Server (Restore)

1. Install Docker/Docker Compose
2. Clone upstream repos:
   ```bash
   git clone -b stable https://github.com/coleam00/local-ai-packaged.git
   ```
3. Clone this backup repo:
   ```bash
   git clone <your-private-repo> /root/backups/server-config-backup
   ```
4. Run restoration:
   ```bash
   cd /root/backups/server-config-backup
   ./restore_configs.sh
   ```
5. Restore Docker volumes (see restore_volumes.sh)
6. Start services

## Directory Structure

- `env-files/` - All .env files preserving directory structure
- `docker-compose/` - Modified docker-compose.yml files
- `scripts/` - Custom scripts
- `configs/` - Service-specific configurations
- `restore_configs.sh` - Automated restoration script

## Security Warning

This directory contains secrets (.env files).

Options:
1. Store in a **private** Git repository only
2. Encrypt sensitive files before committing
3. Use git-crypt or similar for automatic encryption

## Notes

Add notes here about any customizations you've made to upstream repos.
README

echo "Initializing Git repository (if not already)..." | tee -a "$BACKUP_LOG"
# Initialize git repo if it doesn't exist
if [ ! -d "$BACKUP_DIR/.git" ]; then
    cd "$BACKUP_DIR"
    git init

    # Create .gitignore
    cat > .gitignore << 'GITIGNORE'
# Add patterns for files you don't want to commit
# For example, if you want to manually encrypt .env files:
# *.env
GITIGNORE

    git add .
    git commit -m "Initial configuration backup - $(date +%Y-%m-%d)"

    echo ""
    echo "==================================================================="
    echo "Git repository initialized at $BACKUP_DIR"
    echo ""
    echo "IMPORTANT: Set up a remote repository to push backups:"
    echo "  1. Create a PRIVATE repository on GitHub/GitLab"
    echo "  2. Add remote: cd $BACKUP_DIR && git remote add origin <repo-url>"
    echo "  3. Push: git push -u origin main"
    echo ""
    echo "WARNING: This backup contains secrets (.env files)."
    echo "         Only push to PRIVATE repositories!"
    echo "==================================================================="
else
    cd "$BACKUP_DIR"
    git add .
    git commit -m "Config backup - $(date +%Y-%m-%d)" || echo "No changes to commit"

    # Auto-push to remote if configured
    if git remote -v | grep -q origin; then
        echo "Pushing to remote repository..." | tee -a "$BACKUP_LOG"
        if git push 2>&1 | tee -a "$BACKUP_LOG"; then
            echo "  ✓ Successfully pushed to GitHub" | tee -a "$BACKUP_LOG"
        else
            echo "  ⚠️  Failed to push to GitHub (check SSH keys or network)" | tee -a "$BACKUP_LOG"
        fi
    else
        echo "  ⚠️  No git remote configured, skipping push" | tee -a "$BACKUP_LOG"
    fi
fi

echo ""
echo "=== Configuration Backup Complete: $(date) ===" | tee -a "$BACKUP_LOG"
echo "Backup location: $BACKUP_DIR"
echo "Log file: $BACKUP_LOG"
echo ""
echo "Next steps:"
echo "1. Review backed up files in $BACKUP_DIR"
echo "2. Push to your private Git repo (if set up)"
echo "3. Run backup_volumes.sh to backup Docker volumes"
