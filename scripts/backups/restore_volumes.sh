#!/bin/bash
#
# Docker Volume Restoration Script
# Restores Docker volumes from backups
#

set -e

BACKUP_DIR="/root/backups/volumes"
BACKUP_LOG="/var/log/volume_restore.log"

echo "=== Docker Volume Restoration Started: $(date) ===" | tee -a "$BACKUP_LOG"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: Backup directory not found: $BACKUP_DIR" | tee -a "$BACKUP_LOG"
    echo "Have you extracted the combined backup archive?"
    echo "  mkdir -p /root/backups/volumes"
    echo "  tar -xzf docker-volumes-YYYYMMDD_HHMMSS.tar.gz -C /root/backups/volumes"
    exit 1
fi

# List available backups
echo "Available volume backups:" | tee -a "$BACKUP_LOG"
ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | grep -v "_latest.tar.gz" | tee -a "$BACKUP_LOG" || {
    echo "No backup files found in $BACKUP_DIR" | tee -a "$BACKUP_LOG"
    exit 1
}

echo ""
echo "This script will restore Docker volumes from backup."
echo "WARNING: This will OVERWRITE existing volume data!"
echo ""

# Function to restore a single volume
restore_volume() {
    local volume_name=$1
    local backup_file=$2

    if [ ! -f "$backup_file" ]; then
        echo "  ✗ Backup file not found: $backup_file" | tee -a "$BACKUP_LOG"
        return 1
    fi

    echo "Restoring volume: $volume_name..." | tee -a "$BACKUP_LOG"

    # Create volume if it doesn't exist
    docker volume create "$volume_name" >/dev/null 2>&1 || true

    # Restore volume data
    docker run --rm \
        -v "${volume_name}:/data" \
        -v "$BACKUP_DIR:/backup:ro" \
        alpine \
        sh -c "rm -rf /data/* /data/..?* /data/.[!.]* 2>/dev/null || true; cd /data && tar xzf /backup/$(basename "$backup_file")" \
        2>&1 | tee -a "$BACKUP_LOG"

    if [ $? -eq 0 ]; then
        echo "  ✓ Restored $volume_name" | tee -a "$BACKUP_LOG"
        return 0
    else
        echo "  ✗ Failed to restore $volume_name" | tee -a "$BACKUP_LOG"
        return 1
    fi
}

# Interactive mode: ask which volumes to restore
if [ "$1" == "--interactive" ] || [ "$1" == "-i" ]; then
    echo "=== Interactive Restoration Mode ===" | tee -a "$BACKUP_LOG"

    # Get unique volume names from backup files
    for backup in "$BACKUP_DIR"/*_latest.tar.gz; do
        if [ -f "$backup" ]; then
            volume_name=$(basename "$backup" | sed 's/_latest\.tar\.gz$//')

            echo ""
            read -p "Restore volume '$volume_name'? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                restore_volume "$volume_name" "$backup"
            else
                echo "  ⊘ Skipped $volume_name" | tee -a "$BACKUP_LOG"
            fi
        fi
    done

# Auto mode: restore specific volume
elif [ -n "$1" ]; then
    volume_name=$1
    backup_file="$BACKUP_DIR/${volume_name}_latest.tar.gz"

    if [ ! -f "$backup_file" ]; then
        echo "Error: No backup found for volume '$volume_name'" | tee -a "$BACKUP_LOG"
        echo "Available backups:"
        ls -1 "$BACKUP_DIR"/*_latest.tar.gz | sed 's/.*\///' | sed 's/_latest\.tar\.gz$//'
        exit 1
    fi

    echo "WARNING: This will overwrite volume '$volume_name'"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restore_volume "$volume_name" "$backup_file"
    else
        echo "Cancelled" | tee -a "$BACKUP_LOG"
        exit 0
    fi

# Restore all volumes (use with caution!)
elif [ "$1" == "--all" ]; then
    echo "WARNING: This will restore ALL volumes from backup!"
    echo "This will OVERWRITE all existing data!"
    echo ""
    read -p "Are you absolutely sure? Type 'yes' to continue: " confirm

    if [ "$confirm" == "yes" ]; then
        for backup in "$BACKUP_DIR"/*_latest.tar.gz; do
            if [ -f "$backup" ]; then
                volume_name=$(basename "$backup" | sed 's/_latest\.tar\.gz$//')
                restore_volume "$volume_name" "$backup"
            fi
        done
    else
        echo "Cancelled" | tee -a "$BACKUP_LOG"
        exit 0
    fi

# Show usage
else
    echo "Usage:"
    echo "  $0 --interactive          # Interactively choose which volumes to restore"
    echo "  $0 <volume_name>          # Restore a specific volume"
    echo "  $0 --all                  # Restore all volumes (DANGEROUS!)"
    echo ""
    echo "Examples:"
    echo "  $0 --interactive"
    echo "  $0 wordpress_mysql_data"
    echo "  $0 portainer_portainer_data"
    echo ""
    echo "Available volumes to restore:"
    ls -1 "$BACKUP_DIR"/*_latest.tar.gz 2>/dev/null | sed 's/.*\///' | sed 's/_latest\.tar\.gz$//' | sed 's/^/  - /'
    exit 0
fi

echo ""
echo "=== Docker Volume Restoration Complete: $(date) ===" | tee -a "$BACKUP_LOG"
echo "Log file: $BACKUP_LOG"
echo ""
echo "Next steps:"
echo "1. Verify restored data"
echo "2. Start your Docker services"
echo "3. Test that everything works correctly"
