#!/bin/bash
#
# Optimized Docker Volume Backup Script
# Smart tiering, differential backups, cloud sync
#

set -e

BACKUP_DIR="/root/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y%m%d)
BACKUP_LOG="/var/log/volume_backup.log"
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
DAY_OF_MONTH=$(date +%d)

echo "=== Optimized Docker Volume Backup Started: $(date) ===" | tee -a "$BACKUP_LOG"

# Create temp directory for this backup
TEMP_DIR="/tmp/backup_${TIMESTAMP}"
mkdir -p "$TEMP_DIR"

# Tier 1: CRITICAL - Backup daily (cannot recreate)
TIER1_VOLUMES=(
    "wordpress_mysql_data"
    "wordpress_wordpress_data"
    "coolify-db"
    "portainer_portainer_data"
    "supabase_db-config"
)

# Tier 2: IMPORTANT - Backup weekly (configurations)
TIER2_VOLUMES=(
    "filebrowser_filebrowser_config"
    "filebrowser_filebrowser_data"
    "local-ai-packaged_caddy-config"
    "local-ai-packaged_db-config"
    "n8n-mcp_n8n-mcp-data"
    "local-ai-packaged_n8n_storage"
    "coolify-redis"
)

# Tier 3: EXCLUDE - Never backup (transient/recreatable)
EXCLUDE_VOLUMES=(
    "monitoring_netdata_lib"
    "monitoring_netdata_config"
    "local-ai-packaged_langfuse_clickhouse_logs"
    "local-ai-packaged_valkey-data"
    "local-ai-packaged_qdrant_storage"
    "local-ai-packaged_langfuse_postgres_data"
    "local-ai-packaged_langfuse_minio_data"
    "monitoring_uptime_kuma_data"
)

# Function to backup a volume
backup_volume() {
    local volume=$1
    local tier=$2

    if ! docker volume ls --format "{{.Name}}" | grep -q "^${volume}$"; then
        echo "  ⊘ Volume $volume not found, skipping" | tee -a "$BACKUP_LOG"
        return
    fi

    # Check if volume is empty (less than 1KB)
    local size=$(docker run --rm -v "${volume}:/data:ro" alpine du -sb /data | cut -f1)
    if [ "$size" -lt 1024 ]; then
        echo "  ⊘ Volume $volume is empty (<1KB), skipping" | tee -a "$BACKUP_LOG"
        return
    fi

    echo "  Backing up [$tier] $volume..." | tee -a "$BACKUP_LOG"

    # Create backup
    docker run --rm \
        -v "${volume}:/data:ro" \
        -v "$TEMP_DIR:/backup" \
        alpine \
        tar czf "/backup/${volume}.tar.gz" -C /data . \
        2>&1 | grep -v "tar:" | tee -a "$BACKUP_LOG" || true

    if [ -f "$TEMP_DIR/${volume}.tar.gz" ]; then
        local backup_size=$(du -h "$TEMP_DIR/${volume}.tar.gz" | cut -f1)
        echo "    ✓ Backed up $volume ($backup_size)" | tee -a "$BACKUP_LOG"
    else
        echo "    ✗ Failed to backup $volume" | tee -a "$BACKUP_LOG"
    fi
}

# Determine what to backup based on schedule
VOLUMES_TO_BACKUP=()

# Always backup Tier 1 (critical data)
echo "Backing up Tier 1 (CRITICAL) volumes..." | tee -a "$BACKUP_LOG"
for volume in "${TIER1_VOLUMES[@]}"; do
    backup_volume "$volume" "TIER1"
done

# Backup Tier 2 only on Sundays (weekly)
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    echo "" | tee -a "$BACKUP_LOG"
    echo "Sunday detected - Backing up Tier 2 (IMPORTANT) volumes..." | tee -a "$BACKUP_LOG"
    for volume in "${TIER2_VOLUMES[@]}"; do
        backup_volume "$volume" "TIER2"
    done
fi

# Create single combined archive (no double compression)
echo "" | tee -a "$BACKUP_LOG"
echo "Creating combined backup archive..." | tee -a "$BACKUP_LOG"

# Determine backup type for filename
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    BACKUP_TYPE="weekly"
else
    BACKUP_TYPE="daily"
fi

COMBINED_BACKUP="$BACKUP_DIR/backup-${BACKUP_TYPE}-${DATE}.tar.gz"

# Create archive from temp directory
cd "$TEMP_DIR"
tar czf "$COMBINED_BACKUP" *.tar.gz 2>&1 | tee -a "$BACKUP_LOG" || true
cd - > /dev/null

if [ -f "$COMBINED_BACKUP" ]; then
    combined_size=$(du -h "$COMBINED_BACKUP" | cut -f1)
    echo "  ✓ Combined backup created: $COMBINED_BACKUP ($combined_size)" | tee -a "$BACKUP_LOG"

    # Create latest symlink
    ln -sf "$(basename $COMBINED_BACKUP)" "$BACKUP_DIR/backup-latest.tar.gz"
fi

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Smart retention policy
echo "" | tee -a "$BACKUP_LOG"
echo "Applying retention policy..." | tee -a "$BACKUP_LOG"

# Keep daily backups for 7 days
find "$BACKUP_DIR" -name "backup-daily-*.tar.gz" -mtime +7 -exec rm -f {} \; 2>&1 | tee -a "$BACKUP_LOG"
echo "  ✓ Kept last 7 daily backups" | tee -a "$BACKUP_LOG"

# Keep weekly backups for 30 days (4 weeks)
find "$BACKUP_DIR" -name "backup-weekly-*.tar.gz" -mtime +30 -exec rm -f {} \; 2>&1 | tee -a "$BACKUP_LOG"
echo "  ✓ Kept last 4 weekly backups" | tee -a "$BACKUP_LOG"

# Clean up old bloated backups from previous system
if [ -d "$BACKUP_DIR/volumes" ]; then
    echo "  ⚠ Found old backup directory from previous system" | tee -a "$BACKUP_LOG"
fi

# Sync to Google Drive (if configured)
if command -v rclone &> /dev/null && rclone listremotes | grep -q "flourisha"; then
    echo "" | tee -a "$BACKUP_LOG"
    echo "Syncing to Google Drive..." | tee -a "$BACKUP_LOG"

    # Create backups folder in Google Drive if it doesn't exist
    rclone mkdir flourisha:/05_Backups/server-backups 2>&1 | tee -a "$BACKUP_LOG" || true

    # Copy latest backup to Google Drive
    rclone copy "$COMBINED_BACKUP" flourisha:/05_Backups/server-backups \
        --progress \
        --transfers 1 \
        --checkers 1 \
        2>&1 | grep -E "(Transferred:|Checks:|Elapsed)" | tee -a "$BACKUP_LOG" || true

    echo "  ✓ Backup synced to Google Drive" | tee -a "$BACKUP_LOG"
else
    echo "" | tee -a "$BACKUP_LOG"
    echo "  ⚠ Google Drive sync not configured (install rclone)" | tee -a "$BACKUP_LOG"
fi

echo "" | tee -a "$BACKUP_LOG"
echo "=== Backup Complete: $(date) ===" | tee -a "$BACKUP_LOG"
echo "" | tee -a "$BACKUP_LOG"
echo "Summary:" | tee -a "$BACKUP_LOG"
echo "  Backup file: $COMBINED_BACKUP" | tee -a "$BACKUP_LOG"
echo "  Backup size: $(du -h $COMBINED_BACKUP | cut -f1)" | tee -a "$BACKUP_LOG"
echo "  Backup type: $BACKUP_TYPE" | tee -a "$BACKUP_LOG"
echo "  Total backup disk usage: $(du -sh $BACKUP_DIR | cut -f1)" | tee -a "$BACKUP_LOG"
echo "" | tee -a "$BACKUP_LOG"
