---
name: docker-sandbox
description: Execute tasks in local Docker containers using disler patterns. USE WHEN user requests sandbox execution OR building full-stack apps OR testing Phase 2 Docker migration. Provides unlimited runtime and zero cost compared to E2B.
---

# Docker Sandbox Skill

Execute Flourisha tasks in local Docker containers with unlimited runtime and zero cost.

## When to Use This Skill

**USE WHEN**:
- User requests sandbox execution for full-stack app development
- Building calculator, todo, or other full-stack applications
- Testing Phase 2 Docker migration from E2B
- Cost optimization needed (Docker = $0/hr vs E2B = $0.13-0.44/hr)
- Unlimited runtime required (Docker = ∞ vs E2B = 1 hour max)
- Parallel container execution needed for multiple agents

**DO NOT USE WHEN**:
- Phase 1 E2B validation still in progress (defer to E2B)
- User explicitly requests E2B sandboxes
- Docker daemon not available or not running

## Core Commands

All commands use the `docker-sandbox` CLI wrapper (mimics E2B's `sbx` command structure):

### 1. Initialize Container

```bash
docker-sandbox init [--timeout SECONDS] [--use-pool]
```

**Purpose**: Create and start a new Docker sandbox container

**Returns**: Container ID (e.g., `flourisha-sandbox-1701234567`)

**Options**:
- `--timeout SECONDS`: Container lifetime in seconds (default: 3600)
- `--use-pool`: Claim container from pre-warmed pool (faster startup)

**Example**:
```bash
CONTAINER_ID=$(docker-sandbox init --timeout 7200)
echo "Container started: $CONTAINER_ID"
```

**What it does**:
- Creates Ubuntu 22.04 container with Python 3.11, Node 22, SQLite
- Mounts `/workspace` volume
- Exposes ports 8000 (FastAPI), 5173 (Vite), 3000 (Node)
- Returns container ID for subsequent operations

---

### 2. Execute Command

```bash
docker-sandbox exec CONTAINER_ID "command"
```

**Purpose**: Run shell command inside container

**Example**:
```bash
docker-sandbox exec $CONTAINER_ID "python3 --version"
docker-sandbox exec $CONTAINER_ID "npm install vite"
docker-sandbox exec $CONTAINER_ID "cd /workspace && uvicorn main:app --host 0.0.0.0 --port 8000"
```

**What it does**:
- Executes command in container's shell
- Returns stdout/stderr output
- Use for running build commands, tests, starting servers

---

### 3. Upload Files

```bash
docker-sandbox upload CONTAINER_ID local_path remote_path
```

**Purpose**: Copy files from host to container

**Example**:
```bash
docker-sandbox upload $CONTAINER_ID /tmp/app.py /workspace/app.py
docker-sandbox upload $CONTAINER_ID /tmp/frontend/ /workspace/frontend/
```

**What it does**:
- Uses `docker cp` to transfer files
- Supports single files and directories
- Preserves file permissions

---

### 4. Download Files

```bash
docker-sandbox download CONTAINER_ID remote_path local_path
```

**Purpose**: Copy files from container to host

**Example**:
```bash
docker-sandbox download $CONTAINER_ID /workspace/dist/ /tmp/build-output/
docker-sandbox download $CONTAINER_ID /workspace/screenshot.png /tmp/evidence.png
```

**What it does**:
- Retrieves build artifacts, screenshots, logs
- Use for Phase 4 test evidence collection

---

### 5. Kill Container

```bash
docker-sandbox kill CONTAINER_ID
```

**Purpose**: Stop and remove container

**Example**:
```bash
docker-sandbox kill $CONTAINER_ID
```

**What it does**:
- Stops container gracefully
- Removes container and associated resources
- Always run cleanup after task completion

---

### 6. Get Host URL

```bash
docker-sandbox get-host CONTAINER_ID PORT
```

**Purpose**: Get public URL for accessing container services

**Returns**: URL for accessing service (e.g., `http://localhost:5173` or `https://sandbox-CONTAINER_ID.leadingai.info`)

**Example**:
```bash
VITE_URL=$(docker-sandbox get-host $CONTAINER_ID 5173)
API_URL=$(docker-sandbox get-host $CONTAINER_ID 8000)
echo "Frontend: $VITE_URL"
echo "Backend: $API_URL"
```

**What it does**:
- Returns localhost URL for local development
- Returns Tailscale/public URL for remote access
- Use for Phase 4 browser testing validation

---

## Workflow: 4-Phase Pattern

Docker sandboxes follow disler's proven 4-phase pattern (identical to E2B):

### Phase 1: PLAN

**Objective**: Analyze PRD and create implementation plan

**Actions**:
- Read PRD specification
- Identify tech stack requirements
- Plan component architecture
- Define success criteria

**Output**: Implementation plan with file structure

---

### Phase 2: BUILD

**Objective**: Write code and configure services

**Docker Commands**:
```bash
# Initialize container
CONTAINER_ID=$(docker-sandbox init --timeout 3600)

# Upload backend code
docker-sandbox upload $CONTAINER_ID /tmp/backend/ /workspace/backend/

# Install dependencies
docker-sandbox exec $CONTAINER_ID "cd /workspace/backend && pip install -r requirements.txt"

# Upload frontend code
docker-sandbox upload $CONTAINER_ID /tmp/frontend/ /workspace/frontend/

# Install frontend dependencies
docker-sandbox exec $CONTAINER_ID "cd /workspace/frontend && npm install"
```

**Output**: All code uploaded and dependencies installed

---

### Phase 3: HOST

**Objective**: Start services and verify they're running

**Docker Commands**:
```bash
# Start backend (FastAPI)
docker-sandbox exec $CONTAINER_ID "cd /workspace/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &"

# Start frontend (Vite)
docker-sandbox exec $CONTAINER_ID "cd /workspace/frontend && npm run dev -- --host 0.0.0.0 --port 5173 &"

# Get public URLs
API_URL=$(docker-sandbox get-host $CONTAINER_ID 8000)
VITE_URL=$(docker-sandbox get-host $CONTAINER_ID 5173)

echo "Backend: $API_URL"
echo "Frontend: $VITE_URL"
```

**Output**: Services running with accessible URLs

---

### Phase 4: TEST

**Objective**: Validate all success criteria with automated browser testing

**Docker Commands**:
```bash
# Test API endpoint
curl $API_URL/api/health

# Browser automation with Playwright
docker-sandbox exec $CONTAINER_ID "cd /workspace && python3 browser_test.py --url $VITE_URL"

# Download test evidence
docker-sandbox download $CONTAINER_ID /workspace/screenshots/ /tmp/evidence/

# Cleanup
docker-sandbox kill $CONTAINER_ID
```

**Output**: Test results, screenshots, success/failure report

---

## Container Pool Management

For faster startup times, use pre-warmed container pools:

### Claim from Pool

```bash
CONTAINER_ID=$(docker-sandbox init --use-pool)
```

**Benefits**:
- 5-second startup vs 30-second cold start
- Dependencies pre-installed
- Ready for immediate use

### When to Use Pools

**USE POOLS WHEN**:
- Running multiple parallel builds
- Quick validation/testing needed
- Agent delegation with concurrent execution

**CREATE NEW CONTAINERS WHEN**:
- Custom dependencies needed
- Long-running tasks (>1 hour)
- Isolation requirements

---

## Docker vs E2B Comparison

| Feature | E2B | Docker | Winner |
|---------|-----|--------|--------|
| Cost | $0.13-0.44/hr | $0/hr | Docker |
| Runtime limit | 1 hour max | Unlimited | Docker |
| Startup time | ~30s | ~5s (pooled) | Docker |
| Public URLs | Automatic | Manual (Traefik) | E2B |
| Cleanup | Automatic | Manual | E2B |
| Setup | None | Initial setup | E2B |
| Control | Limited | Full | Docker |
| Production ready | Yes | Yes (with hardening) | Tie |

**Recommendation**: Use Docker for cost optimization and unlimited runtime. Use E2B for quick validation/prototyping.

---

## Reference Documentation

**Primary Reference**:
`/root/flourisha/00_AI_Brain/documentation/PHASE2_DOCKER_MIGRATION_PLAN.md`

**Additional Resources**:
- Docker sandbox template: `/root/flourisha/01f_Flourisha_Projects/docker-sandbox-template/`
- CLI wrapper script: `/root/flourisha/scripts/docker-sandbox-cli.sh`
- Cleanup automation: `/root/flourisha/scripts/docker-sandbox-cleanup.sh`

---

## Troubleshooting

### Container won't start

```bash
# Check Docker daemon
systemctl status docker

# View logs
docker logs $CONTAINER_ID

# Restart daemon
systemctl restart docker
```

### Port already in use

```bash
# Find conflicting container
docker ps | grep 5173

# Kill old container
docker-sandbox kill OLD_CONTAINER_ID
```

### Out of disk space

```bash
# Cleanup old containers
docker system prune -a --volumes -f
```

---

## Security Considerations

1. **Resource limits**: Containers have CPU/memory limits to prevent resource exhaustion
2. **Network isolation**: Each sandbox runs in isolated Docker network
3. **Automated cleanup**: Cron job removes containers older than 2 hours
4. **Non-root user**: Code runs as `coder` user (not root)

---

## Success Criteria

**Container initialized successfully when**:
- Container ID returned
- Docker daemon responsive
- Ports exposed correctly
- Volume mounted at `/workspace`

**Build completed successfully when**:
- All dependencies installed without errors
- Code uploaded to container
- Services start without crashes

**Tests passed successfully when**:
- All API endpoints return expected responses
- Browser automation completes without errors
- Screenshots show correct UI state
- Success criteria from PRD validated

---

## Example: Full Calculator Build

```bash
# Phase 1: PLAN (analyze PRD)
# (This happens in agent planning, no Docker needed)

# Phase 2: BUILD
CONTAINER_ID=$(docker-sandbox init --timeout 3600)
docker-sandbox upload $CONTAINER_ID /tmp/calculator/ /workspace/
docker-sandbox exec $CONTAINER_ID "cd /workspace/backend && pip install -r requirements.txt"
docker-sandbox exec $CONTAINER_ID "cd /workspace/frontend && npm install"

# Phase 3: HOST
docker-sandbox exec $CONTAINER_ID "cd /workspace/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &"
docker-sandbox exec $CONTAINER_ID "cd /workspace/frontend && npm run dev -- --host 0.0.0.0 --port 5173 &"

API_URL=$(docker-sandbox get-host $CONTAINER_ID 8000)
VITE_URL=$(docker-sandbox get-host $CONTAINER_ID 5173)

# Phase 4: TEST
curl $API_URL/api/calculate -X POST -d '{"a": 5, "b": 3, "operation": "add"}'
docker-sandbox exec $CONTAINER_ID "python3 /workspace/tests/browser_test.py --url $VITE_URL"
docker-sandbox download $CONTAINER_ID /workspace/screenshots/ /tmp/evidence/

# Cleanup
docker-sandbox kill $CONTAINER_ID
```

---

## Notes

- **Always cleanup**: Run `docker-sandbox kill` after task completion
- **Monitor resources**: Check container resource usage with `docker stats`
- **Use pools for speed**: Pre-warmed containers start 6× faster
- **Document evidence**: Download screenshots and logs for validation
- **Cost optimization**: Docker saves $0.13-0.44/hour compared to E2B
