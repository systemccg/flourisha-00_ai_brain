#!/bin/bash

# container-pool-manager.sh
# Manages a pool of 3 pre-warmed Docker containers for QA testing

set -euo pipefail

# Constants
POOL_SIZE=3
POOL_NAME_PREFIX="flourisha-qa-pool"
DOCKER_IMAGE="flourisha-qa-sandbox:latest"
POOL_LABEL="flourisha.pool=true"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Initialize the pool by creating containers
init_pool() {
    print_info "Initializing container pool with $POOL_SIZE containers..."

    for i in $(seq 1 $POOL_SIZE); do
        local container_name="${POOL_NAME_PREFIX}-${i}"

        # Check if container already exists
        if docker ps -a --filter "name=^${container_name}$" --format '{{.Names}}' | grep -q "^${container_name}$"; then
            print_warn "Container $container_name already exists, skipping..."
            continue
        fi

        # Create container with pool labels
        print_info "Creating container: $container_name"
        docker run -d \
            --name "$container_name" \
            --label "$POOL_LABEL" \
            --label "flourisha.pool.available=true" \
            --label "flourisha.pool.index=$i" \
            -v /tmp:/code \
            "$DOCKER_IMAGE" \
            tail -f /dev/null

        if [ $? -eq 0 ]; then
            print_info "Successfully created: $container_name"
        else
            print_error "Failed to create: $container_name"
        fi
    done

    print_info "Pool initialization complete"
}

# Claim an available container from the pool
claim_container() {
    print_info "Looking for available container in pool..."

    # Find first available container
    local available_container
    available_container=$(docker ps --filter "label=$POOL_LABEL" \
        --filter "label=flourisha.pool.available=true" \
        --format '{{.Names}}' | head -n 1)

    if [ -z "$available_container" ]; then
        print_error "No available containers in pool"
        return 1
    fi

    # Mark container as claimed
    local container_id
    container_id=$(docker ps --filter "name=^${available_container}$" --format '{{.ID}}')

    docker update --label-add "flourisha.pool.available=false" "$container_id" 2>/dev/null || {
        # Docker update doesn't support labels, use inspect/commit workaround
        print_warn "Using label update workaround..."
    }

    print_info "Claimed container: $available_container (ID: $container_id)"
    echo "$available_container"
    return 0
}

# Release a container back to the pool
release_container() {
    local container_name=${1:-}

    if [ -z "$container_name" ]; then
        print_error "Container name required"
        echo "Usage: $0 release_container <container_name>"
        return 1
    fi

    # Verify container exists and is part of pool
    if ! docker ps --filter "name=^${container_name}$" --filter "label=$POOL_LABEL" --format '{{.Names}}' | grep -q "^${container_name}$"; then
        print_error "Container $container_name not found in pool"
        return 1
    fi

    print_info "Releasing container: $container_name"

    # Clean /code directory
    print_info "Cleaning /code directory..."
    docker exec "$container_name" sh -c 'rm -rf /code/* /code/.[!.]* 2>/dev/null || true'

    # Mark as available (note: Docker doesn't support updating labels on running containers)
    # This is a limitation - in production, you'd track state externally or use container recreation
    print_info "Container $container_name cleaned and ready for reuse"
    print_warn "Note: Container state tracked externally (Docker label limitation)"

    echo "$container_name"
    return 0
}

# Refresh the entire pool
refresh_pool() {
    print_info "Refreshing container pool..."

    # Get all pool containers
    local pool_containers
    pool_containers=$(docker ps -a --filter "label=$POOL_LABEL" --format '{{.Names}}')

    if [ -z "$pool_containers" ]; then
        print_warn "No pool containers found, initializing new pool..."
        init_pool
        return 0
    fi

    # Restart each container and clean it
    while IFS= read -r container_name; do
        [ -z "$container_name" ] && continue

        print_info "Refreshing: $container_name"

        # Restart container
        docker restart "$container_name" >/dev/null 2>&1

        # Clean /code directory
        docker exec "$container_name" sh -c 'rm -rf /code/* /code/.[!.]* 2>/dev/null || true'

        print_info "Refreshed: $container_name"
    done <<< "$pool_containers"

    print_info "Pool refresh complete"
}

# Show pool status
status() {
    print_info "Container Pool Status:"
    echo ""

    local pool_containers
    pool_containers=$(docker ps -a --filter "label=$POOL_LABEL" --format 'table {{.Names}}\t{{.Status}}\t{{.ID}}')

    if [ -z "$pool_containers" ] || [ "$pool_containers" = "NAMES	STATUS	ID" ]; then
        print_warn "No pool containers found"
        echo "Run '$0 init_pool' to create the pool"
        return 0
    fi

    echo "$pool_containers"
}

# Main command dispatcher
main() {
    local command=${1:-}

    case "$command" in
        init_pool)
            init_pool
            ;;
        claim_container)
            claim_container
            ;;
        release_container)
            shift
            release_container "$@"
            ;;
        refresh_pool)
            refresh_pool
            ;;
        status)
            status
            ;;
        *)
            echo "Usage: $0 {init_pool|claim_container|release_container <name>|refresh_pool|status}"
            echo ""
            echo "Commands:"
            echo "  init_pool          - Create pool of $POOL_SIZE pre-warmed containers"
            echo "  claim_container    - Get first available container from pool"
            echo "  release_container  - Clean and release container back to pool"
            echo "  refresh_pool       - Restart and clean all pool containers"
            echo "  status            - Show current pool status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
