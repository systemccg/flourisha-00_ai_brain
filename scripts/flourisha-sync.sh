#!/bin/bash
# PAI Flourisha Bidirectional Sync (Using rclone bisync)
# True bidirectional sync with state tracking
# Correctly handles new files AND deletions on both sides

set -euo pipefail

FLOURISHA_REMOTE="flourisha:"
FLOURISHA_LOCAL="/root/flourisha"
LOG_FILE="/var/log/pai_flourisha_bisync.log"
BACKUP_DIR1="flourisha:ToBeDeleted"
BACKUP_DIR2="/root/flourisha/ToBeDeleted"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${2:-$NC}$1${NC}" | tee -a "$LOG_FILE"
}

# Parse command line arguments
DRY_RUN=""
TEST_MODE=""
RESYNC=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            log "🔍 DRY RUN MODE - No changes will be made" "$YELLOW"
            shift
            ;;
        --test)
            TEST_MODE="yes"
            FLOURISHA_REMOTE="flourisha:00_SYNC_TEST"
            FLOURISHA_LOCAL="/root/flourisha/00_SYNC_TEST"
            BACKUP_DIR1="flourisha:00_SYNC_TEST/ToBeDeleted"
            BACKUP_DIR2="/root/flourisha/00_SYNC_TEST/ToBeDeleted"
            log "🧪 TEST MODE - Using 00_SYNC_TEST folder only" "$BLUE"
            shift
            ;;
        --resync)
            RESYNC="--resync"
            log "🔄 RESYNC MODE - Initializing bisync state" "$YELLOW"
            shift
            ;;
        *)
            log "Unknown option: $1" "$RED"
            echo "Usage: $0 [--dry-run] [--test] [--resync]"
            exit 1
            ;;
    esac
done

log "=======================================" "$BLUE"
log "PAI Flourisha BISYNC (Bidirectional)" "$BLUE"
log "Started: $(date)" "$BLUE"
log "Remote: $FLOURISHA_REMOTE" "$BLUE"
log "Local: $FLOURISHA_LOCAL" "$BLUE"
log "=======================================" "$BLUE"

# Ensure directories exist
mkdir -p "$FLOURISHA_LOCAL"
mkdir -p "$BACKUP_DIR2"

# Run bisync
log "\n🔄 Running bidirectional sync..." "$BLUE"

BISYNC_CMD="rclone bisync \"$FLOURISHA_LOCAL\" \"$FLOURISHA_REMOTE\" \
    --exclude \"node_modules/\" \
    --exclude \"venv/\" \
    --exclude \".venv/\" \
    --exclude \"**/node_modules/\" \
    --exclude \"**/venv/\" \
    --exclude \".obsidian/**\" \
    --exclude \"ToBeDeleted/**\" \
    --exclude \"**/*.CONFLICT-*\" \
    --interactive=false \
    $RESYNC \
    $DRY_RUN"

# Execute bisync
if eval $BISYNC_CMD 2>&1 | tee -a "$LOG_FILE"; then
    log "\n✅ Bidirectional sync successful!" "$GREEN"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
        log "\n⚠️  Bisync needs initialization - run with --resync first:" "$YELLOW"
        log "  $0 --resync ${TEST_MODE:+--test}" "$YELLOW"
    else
        log "\n❌ Sync failed with exit code $EXIT_CODE" "$RED"
    fi
    exit $EXIT_CODE
fi

# Summary
log "\n=======================================" "$GREEN"
log "Sync Complete: $(date)" "$GREEN"
log "Files synced bidirectionally" "$GREEN"
log "Log file: $LOG_FILE" "$GREEN"
log "=======================================" "$GREEN"

log "\n💡 How it works:"
log "  ✓ New files on either side → copied to other side"
log "  ✓ Deleted files on either side → deleted from other side"
log "  ✓ Modified files → newer version wins"
log "  ✓ Conflicts → both versions kept with numbers"
