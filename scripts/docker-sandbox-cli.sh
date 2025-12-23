#!/bin/bash
#
# Docker Sandbox CLI Wrapper
# Mirrors E2B sbx commands using Docker containers
#
# Usage:
#   docker-sandbox-cli.sh init                    - Create new sandbox container
#   docker-sandbox-cli.sh exec <id> <command>     - Execute command in container
#   docker-sandbox-cli.sh upload <id> <src> <dst> - Upload file to container
#   docker-sandbox-cli.sh download <id> <src> <dst> - Download file from container
#   docker-sandbox-cli.sh kill <id>               - Stop and remove container
#   docker-sandbox-cli.sh get-host <id>           - Get public URL for container
#

set -e

# Source central configuration (contains SERVER_IP and other critical settings)
CONFIG_FILE="/root/flourisha/00_AI_Brain/.flourisha-config"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "ERROR: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

COMMAND="${1}"
CONTAINER_ID="${2}"

# Local aliases for compatibility with rest of script
IMAGE="$SANDBOX_IMAGE"
RAM_LIMIT="$SANDBOX_RAM"
CPU_LIMIT="$SANDBOX_CPU"
STORAGE_PATH="$SANDBOX_STORAGE_PATH"
NETWORK_PREFIX="$SANDBOX_NETWORK_PREFIX"
CONTAINER_PREFIX="$SANDBOX_CONTAINER_PREFIX"
BASE_DOMAIN="$SERVER_HOSTNAME"

# Ensure storage directory exists
ensure_storage() {
    if [ ! -d "${STORAGE_PATH}" ]; then
        mkdir -p "${STORAGE_PATH}"
        log_info "Created storage directory: ${STORAGE_PATH}"
    fi
}

# Get short container ID (first 12 chars)
get_short_id() {
    local full_id="$1"
    echo "${full_id:0:12}"
}

# Initialize new sandbox container
init_sandbox() {
    ensure_storage

    local timestamp=$(date +%s)
    local container_name="${CONTAINER_PREFIX}-${timestamp}"
    local network_name="${NETWORK_PREFIX}-${timestamp}"

    log_info "Creating sandbox container: ${container_name}"

    # Create dedicated network for this sandbox
    log_info "Creating network: ${network_name}"
    docker network create "${network_name}" >/dev/null 2>&1 || {
        log_warn "Network creation failed, using default bridge network"
        network_name="bridge"
    }

    # Create container with specified resources
    # Container will be on both its own network and the Traefik network for routing
    local container_id=$(docker run -d \
        --name "${container_name}" \
        --network "${network_name}" \
        --memory="${RAM_LIMIT}" \
        --cpus="${CPU_LIMIT}" \
        --mount type=bind,source="${STORAGE_PATH}",target=/code \
        --workdir /code \
        --label "traefik.enable=true" \
        --label "traefik.http.services.${container_name}.loadbalancer.server.port=8000" \
        "${IMAGE}" \
        sleep infinity)

    if [ -z "${container_id}" ]; then
        log_error "Failed to create container"
        exit 1
    fi

    # Connect to Traefik network so Traefik can route to this container
    log_info "Connecting container to Traefik network for routing..."
    docker network connect traefik "${container_id}" >/dev/null 2>&1 || {
        log_warn "Could not connect to Traefik network (may not exist or already connected)"
    }

    local short_id=$(get_short_id "${container_id}")

    # Add dynamic Traefik routing for this specific sandbox
    # Update dynamic-conf.yml to add a route for this container
    log_info "Configuring Traefik routing for qa-${short_id}.leadingai.info..."

    # Read current Traefik config
    local traefik_config="/root/traefik/dynamic-conf.yml"
    local temp_config="/tmp/traefik-update-$$.yml"

    # Add new route and service to config dynamically
    if ! grep -q "qa-${short_id}:" "${traefik_config}"; then
        # Build the complete configuration to insert
        local router_config="    qa-${short_id}:"
        router_config+=$'\n'"      rule: \"Host(\`qa-${short_id}.leadingai.info\`)\""
        router_config+=$'\n'"      service: qa-backend-${short_id}"
        router_config+=$'\n'"      entryPoints:"
        router_config+=$'\n'"        - websecure"
        router_config+=$'\n'"      tls:"
        router_config+=$'\n'"        certResolver: letsencrypt"
        router_config+=$'\n'

        local service_config="    qa-backend-${short_id}:"
        service_config+=$'\n'"      loadBalancer:"
        service_config+=$'\n'"        servers:"
        service_config+=$'\n'"          - url: \"http://${container_name}.traefik:8000\""
        service_config+=$'\n'

        # Create a backup
        cp "${traefik_config}" "${traefik_config}.backup"

        # Use awk to insert at correct positions (with proper escaping for backticks)
        awk -v router="$router_config" -v service="$service_config" '
          /^  services:/ && !added_router {
            print router;
            added_router = 1;
          }
          /^  middlewares:/ && !added_service {
            print service;
            added_service = 1;
          }
          { print }
        ' "${traefik_config}.backup" > "${traefik_config}.tmp" && mv "${traefik_config}.tmp" "${traefik_config}"

        rm "${traefik_config}.backup"

        log_success "Traefik route added for qa-${short_id}.leadingai.info"
    else
        log_warn "Route for qa-${short_id} already exists in Traefik config"
    fi

    log_success "Container created successfully"
    log_info "Container ID: ${container_id}"
    log_info "Short ID: ${short_id}"
    log_info "Container Name: ${container_name}"
    log_info "Network: ${network_name}"
    log_info "Traefik Network: traefik (via Docker provider)"
    log_info "RAM Limit: ${RAM_LIMIT}"
    log_info "CPU Limit: ${CPU_LIMIT}"
    log_info "Storage Mount: ${STORAGE_PATH} -> /code"
    log_info "Traefik Labels: enabled, port 8000"

    # Output container ID for programmatic use
    echo "${container_id}"
}

# Execute command in sandbox
exec_command() {
    if [ -z "${CONTAINER_ID}" ]; then
        log_error "Container ID required"
        echo "Usage: $0 exec <container_id> <command>"
        exit 1
    fi

    shift 2  # Remove 'exec' and container_id from arguments
    local command="$@"

    if [ -z "${command}" ]; then
        log_error "Command required"
        echo "Usage: $0 exec <container_id> <command>"
        exit 1
    fi

    log_info "Executing command in container ${CONTAINER_ID}"
    log_info "Command: ${command}"

    # Execute command and capture output
    docker exec -i "${CONTAINER_ID}" bash -c "${command}"
}

# Upload file to sandbox
upload_file() {
    if [ -z "${CONTAINER_ID}" ]; then
        log_error "Container ID required"
        echo "Usage: $0 upload <container_id> <source_path> <dest_path>"
        exit 1
    fi

    local source_path="$3"
    local dest_path="$4"

    if [ -z "${source_path}" ] || [ -z "${dest_path}" ]; then
        log_error "Source and destination paths required"
        echo "Usage: $0 upload <container_id> <source_path> <dest_path>"
        exit 1
    fi

    if [ ! -e "${source_path}" ]; then
        log_error "Source path does not exist: ${source_path}"
        exit 1
    fi

    log_info "Uploading to container ${CONTAINER_ID}"
    log_info "Source: ${source_path}"
    log_info "Destination: ${dest_path}"

    docker cp "${source_path}" "${CONTAINER_ID}:${dest_path}"

    if [ $? -eq 0 ]; then
        log_success "File uploaded successfully"
    else
        log_error "Upload failed"
        exit 1
    fi
}

# Download file from sandbox
download_file() {
    if [ -z "${CONTAINER_ID}" ]; then
        log_error "Container ID required"
        echo "Usage: $0 download <container_id> <source_path> <dest_path>"
        exit 1
    fi

    local source_path="$3"
    local dest_path="$4"

    if [ -z "${source_path}" ] || [ -z "${dest_path}" ]; then
        log_error "Source and destination paths required"
        echo "Usage: $0 download <container_id> <source_path> <dest_path>"
        exit 1
    fi

    log_info "Downloading from container ${CONTAINER_ID}"
    log_info "Source: ${source_path}"
    log_info "Destination: ${dest_path}"

    docker cp "${CONTAINER_ID}:${source_path}" "${dest_path}"

    if [ $? -eq 0 ]; then
        log_success "File downloaded successfully"
    else
        log_error "Download failed"
        exit 1
    fi
}

# Kill and remove sandbox
kill_sandbox() {
    if [ -z "${CONTAINER_ID}" ]; then
        log_error "Container ID required"
        echo "Usage: $0 kill <container_id>"
        exit 1
    fi

    log_info "Stopping container ${CONTAINER_ID}"

    # Get container name to find associated network
    local container_name=$(docker inspect --format='{{.Name}}' "${CONTAINER_ID}" 2>/dev/null | sed 's/^\///')
    local network_name=$(docker inspect --format='{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}' "${CONTAINER_ID}" 2>/dev/null | grep "${NETWORK_PREFIX}" || echo "")

    # Stop container
    docker kill "${CONTAINER_ID}" >/dev/null 2>&1 || log_warn "Container already stopped"

    # Remove container
    docker rm "${CONTAINER_ID}" >/dev/null 2>&1 || log_warn "Container already removed"

    log_success "Container stopped and removed"

    # Clean up network if it was created for this sandbox
    if [ -n "${network_name}" ] && [ "${network_name}" != "bridge" ]; then
        log_info "Removing network: ${network_name}"
        docker network rm "${network_name}" >/dev/null 2>&1 || log_warn "Network cleanup failed or already removed"
    fi

    log_success "Sandbox terminated successfully"
}

# Get public host URL
get_host_url() {
    if [ -z "${CONTAINER_ID}" ]; then
        log_error "Container ID required"
        echo "Usage: $0 get-host <container_id>"
        exit 1
    fi

    # Verify container exists
    if ! docker inspect "${CONTAINER_ID}" >/dev/null 2>&1; then
        log_error "Container ${CONTAINER_ID} not found"
        exit 1
    fi

    local short_id=$(get_short_id "${CONTAINER_ID}")
    local public_url="https://qa-${short_id}.${BASE_DOMAIN}"

    log_info "Container ID: ${CONTAINER_ID}"
    log_info "Short ID: ${short_id}"

    # Output URL for programmatic use
    echo "${public_url}"
}

# Show usage information
show_usage() {
    cat << EOF
Docker Sandbox CLI Wrapper

Usage:
    $0 <command> [arguments]

Commands:
    init                           Create new sandbox container
                                   Returns: container_id

    exec <id> <command>            Execute command in container
                                   Example: $0 exec abc123 "ls -la"

    upload <id> <src> <dst>        Upload file to container
                                   Example: $0 upload abc123 ./file.txt /code/file.txt

    download <id> <src> <dst>      Download file from container
                                   Example: $0 download abc123 /code/output.txt ./output.txt

    kill <id>                      Stop and remove container
                                   Example: $0 kill abc123

    get-host <id>                  Get public URL for container
                                   Returns: https://qa-{short_id}.leadingai.info
                                   Example: $0 get-host abc123

Configuration:
    RAM Limit:      ${RAM_LIMIT}
    CPU Limit:      ${CPU_LIMIT}
    Storage Path:   ${STORAGE_PATH}
    Base Domain:    ${BASE_DOMAIN}

Examples:
    # Create new sandbox
    SANDBOX_ID=\$($0 init)

    # Execute command
    $0 exec \${SANDBOX_ID} "apt-get update && apt-get install -y python3"

    # Upload file
    $0 upload \${SANDBOX_ID} ./script.py /code/script.py

    # Execute script
    $0 exec \${SANDBOX_ID} "python3 /code/script.py"

    # Download results
    $0 download \${SANDBOX_ID} /code/results.txt ./results.txt

    # Get public URL
    $0 get-host \${SANDBOX_ID}

    # Cleanup
    $0 kill \${SANDBOX_ID}

EOF
}

# Main command dispatcher
case "${COMMAND}" in
    init)
        init_sandbox
        ;;
    exec)
        exec_command "$@"
        ;;
    upload)
        upload_file "$@"
        ;;
    download)
        download_file "$@"
        ;;
    kill)
        kill_sandbox
        ;;
    get-host)
        get_host_url
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: ${COMMAND}"
        echo ""
        show_usage
        exit 1
        ;;
esac
