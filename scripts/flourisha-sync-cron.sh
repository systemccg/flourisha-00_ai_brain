#!/bin/bash
# Flourisha Sync Cron Wrapper
# Runs every 15 minutes with minimal logging to prevent log spam
# Logs only errors and sync completion summary

LOG_FILE="/var/log/pai_flourisha_sync_cron.log"

# Run sync and capture output
OUTPUT=$(/root/.claude/scripts/flourisha-sync.sh 2>&1)
EXIT_CODE=$?

# Log timestamp and result
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron sync started"

    if [ $EXIT_CODE -eq 0 ]; then
        # Extract success message only
        echo "$OUTPUT" | grep -E "✅|Sync Complete" || echo "Sync completed successfully"
    else
        echo "❌ Sync failed with exit code $EXIT_CODE"
        echo "$OUTPUT"
    fi
    echo "---"
} >> "$LOG_FILE"

exit $EXIT_CODE
