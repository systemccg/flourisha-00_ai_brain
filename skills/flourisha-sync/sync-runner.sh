#!/bin/bash

# Flourisha Sync Runner
# Automated daily sync of Flourisha to Google Drive
# Runs via cron job

LOG_FILE="/var/log/flourisha-sync.log"
LOCK_FILE="/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck"
LOCK_MAX_AGE=300  # 5 minutes

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log start
{
    echo ""
    echo "================================"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting flourisha-sync"
    echo "================================"
} >> "$LOG_FILE"

# Function to cleanup stale lock file
cleanup_stale_lock() {
    if [ -f "$LOCK_FILE" ]; then
        LOCK_AGE=$(($(date +%s) - $(stat -c%Y "$LOCK_FILE" 2>/dev/null || stat -f%m "$LOCK_FILE")))

        if [ "$LOCK_AGE" -gt "$LOCK_MAX_AGE" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Removing stale lock file (age: ${LOCK_AGE}s)" >> "$LOG_FILE"
            rclone deletefile "$LOCK_FILE" 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
}

# Cleanup stale locks
cleanup_stale_lock

# Run the actual sync
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Executing rclone bisync..."
    rclone bisync /root/flourisha flourisha: \
        --exclude "node_modules/" \
        --exclude "venv/" \
        --exclude ".venv/" \
        --exclude "**/node_modules/" \
        --exclude "**/venv/" \
        --resync \
        --interactive=false \
        --log-level INFO
} >> "$LOG_FILE" 2>&1

# Capture exit code
EXIT_CODE=$?

# Log result
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync completed with exit code: $EXIT_CODE"

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ SUCCESS: Flourisha synchronized to Google Drive"
    else
        echo "⚠️ WARNING: Sync completed with errors (exit code: $EXIT_CODE)"
        echo "Check log for details: $LOG_FILE"
    fi

    echo "================================"
    echo ""
} >> "$LOG_FILE"

exit $EXIT_CODE
