#!/bin/bash
#
# Full Server Backup Script
# Runs both configuration and volume backups
#

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="/var/log/full_backup.log"

echo "=====================================" | tee -a "$BACKUP_LOG"
echo "=== Full Server Backup Started ===" | tee -a "$BACKUP_LOG"
echo "=== $(date) ===" | tee -a "$BACKUP_LOG"
echo "=====================================" | tee -a "$BACKUP_LOG"
echo "" | tee -a "$BACKUP_LOG"

# Step 1: Backup configurations
echo "Step 1/2: Backing up configurations..." | tee -a "$BACKUP_LOG"
if [ -f /root/backups/backup_configs.sh ]; then
    /root/backups/backup_configs.sh 2>&1 | tee -a "$BACKUP_LOG"
else
    echo "ERROR: backup_configs.sh not found" | tee -a "$BACKUP_LOG"
    exit 1
fi

echo "" | tee -a "$BACKUP_LOG"

# Step 2: Backup Docker volumes (using optimized script)
echo "Step 2/2: Backing up Docker volumes..." | tee -a "$BACKUP_LOG"
if [ -f /root/backups/backup_volumes_optimized.sh ]; then
    /root/backups/backup_volumes_optimized.sh 2>&1 | tee -a "$BACKUP_LOG"
else
    echo "ERROR: backup_volumes_optimized.sh not found" | tee -a "$BACKUP_LOG"
    exit 1
fi

echo "" | tee -a "$BACKUP_LOG"
echo "=====================================" | tee -a "$BACKUP_LOG"
echo "=== Full Server Backup Complete ===" | tee -a "$BACKUP_LOG"
echo "=== $(date) ===" | tee -a "$BACKUP_LOG"
echo "=====================================" | tee -a "$BACKUP_LOG"

# Summary
echo "" | tee -a "$BACKUP_LOG"
echo "Backup Summary:" | tee -a "$BACKUP_LOG"
echo "  - Configurations: /root/backups/server-config-backup/" | tee -a "$BACKUP_LOG"
echo "  - Docker Volumes: /root/backups/backup-*.tar.gz" | tee -a "$BACKUP_LOG"
echo "  - Full Log: $BACKUP_LOG" | tee -a "$BACKUP_LOG"
echo "" | tee -a "$BACKUP_LOG"

# Check if config backup has git remote configured
if [ -d /root/backups/server-config-backup/.git ]; then
    cd /root/backups/server-config-backup
    if git remote -v | grep -q origin; then
        echo "REMINDER: Push config backup to remote repository:" | tee -a "$BACKUP_LOG"
        echo "  cd /root/backups/server-config-backup && git push" | tee -a "$BACKUP_LOG"
    else
        echo "WARNING: No git remote configured for config backup!" | tee -a "$BACKUP_LOG"
        echo "  Set up a private repo and add remote:" | tee -a "$BACKUP_LOG"
        echo "  cd /root/backups/server-config-backup" | tee -a "$BACKUP_LOG"
        echo "  git remote add origin <your-private-repo-url>" | tee -a "$BACKUP_LOG"
        echo "  git push -u origin main" | tee -a "$BACKUP_LOG"
    fi
fi

echo "" | tee -a "$BACKUP_LOG"
echo "IMPORTANT: Copy backups off-server for disaster recovery!" | tee -a "$BACKUP_LOG"

# Get most recent combined backup
LATEST_COMBINED=$(ls -t /root/backups/backup-*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_COMBINED" ]; then
    size=$(du -h "$LATEST_COMBINED" | cut -f1)
    echo "Latest combined backup: $LATEST_COMBINED ($size)" | tee -a "$BACKUP_LOG"
fi
