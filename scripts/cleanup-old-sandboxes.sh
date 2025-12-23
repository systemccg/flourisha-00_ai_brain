#!/bin/bash

# cleanup-old-sandboxes.sh
# Removes Docker containers with name pattern "flourisha-qa-*" older than 24 hours

set -euo pipefail

# Constants
MAX_AGE_SECONDS=86400  # 24 hours
CONTAINER_PATTERN="flourisha-qa-"
LOG_FILE="/var/log/flourisha-cleanup.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to calculate container age in seconds
get_container_age() {
    local container_id=$1
    local created_at
    created_at=$(docker inspect --format='{{.Created}}' "$container_id" 2>/dev/null || echo "")

    if [ -z "$created_at" ]; then
        echo "0"
        return
    fi

    local created_timestamp
    created_timestamp=$(date -d "$created_at" +%s 2>/dev/null || echo "0")
    local current_timestamp
    current_timestamp=$(date +%s)
    local age=$((current_timestamp - created_timestamp))

    echo "$age"
}

# Main cleanup logic
main() {
    log_message "Starting cleanup of old flourisha-qa-* containers"

    # Get all containers matching the pattern (running or stopped)
    local containers
    containers=$(docker ps -a --filter "name=${CONTAINER_PATTERN}" --format "{{.ID}} {{.Names}}" 2>/dev/null || echo "")

    if [ -z "$containers" ]; then
        log_message "No containers found matching pattern: ${CONTAINER_PATTERN}*"
        return 0
    fi

    local removed_count=0
    local checked_count=0

    # Process each container
    while IFS= read -r line; do
        [ -z "$line" ] && continue

        local container_id
        container_id=$(echo "$line" | awk '{print $1}')
        local container_name
        container_name=$(echo "$line" | awk '{print $2}')

        checked_count=$((checked_count + 1))

        # Get container age
        local age_seconds
        age_seconds=$(get_container_age "$container_id")

        if [ "$age_seconds" -ge "$MAX_AGE_SECONDS" ]; then
            log_message "Removing container: $container_name (ID: $container_id, Age: ${age_seconds}s)"

            if docker rm -f "$container_id" >/dev/null 2>&1; then
                log_message "Successfully removed: $container_name"
                removed_count=$((removed_count + 1))
            else
                log_message "ERROR: Failed to remove: $container_name"
            fi
        else
            local age_hours=$((age_seconds / 3600))
            log_message "Skipping container: $container_name (Age: ${age_hours}h, ${age_seconds}s)"
        fi
    done <<< "$containers"

    log_message "Cleanup complete. Checked: $checked_count, Removed: $removed_count"
}

# Run main function
main "$@"
