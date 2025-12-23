---
name: docker-sandbox-agent
description: Delegate full-stack app building and testing to Docker containers. USE WHEN sub-agents need sandbox execution OR building full-stack apps OR context window management. Provides parallel multi-container orchestration using docker-sandbox commands.
---

# Docker Sandbox Agent Skill

## Overview
This skill handles agent delegation patterns for using Docker sandboxes efficiently. Coordinates parallel container usage, pool management, and context optimization.

## When to Use

**Use docker-sandbox-agent when:**
- Delegating work to sub-agents that need sandbox execution
- Building multiple full-stack apps in parallel
- Main agent context window is under pressure
- Sub-agents need immediate container access (use pool)

**vs docker-sandbox skill:**
- docker-sandbox: Direct CLI operations on containers
- docker-sandbox-agent: Orchestration and delegation patterns

## Delegation Patterns

### Pattern 1: Parallel Multi-App Building
Build 3 different apps simultaneously using 3 containers:
1. Launch 3 parallel engineer agents
2. Each agent claims container: `docker-sandbox init --use-pool`
3. Each agent builds their app independently
4. Agents release containers when done: `docker-sandbox kill CONTAINER_ID`

### Pattern 2: Specialized Container Roles
- Pool Container 1: Python/FastAPI development
- Pool Container 2: Node.js/React development
- Pool Container 3: Full-stack testing

Sub-agents request specific container type.

### Pattern 3: Context Window Optimization
When main agent context gets high:
1. Offload build work to sub-agent
2. Sub-agent claims container: `docker-sandbox init --use-pool`
3. Sub-agent performs build, returns just the URL
4. Main agent focuses on testing/validation

## Pool Management

### Claiming a Container
```bash
CONTAINER=$(/root/flourisha/00_AI_Brain/scripts/docker-sandbox-cli.sh init --use-pool)
```

### Releasing a Container
```bash
/root/flourisha/00_AI_Brain/scripts/docker-sandbox-cli.sh kill $CONTAINER
```

### Checking Pool Status
```bash
docker ps --filter "label=flourisha.pool=true" --format "{{.Names}} {{.Label \"flourisha.pool.available\"}}"
```

## Sub-Agent Prompt Templates

### For Full-Stack App Building
"Build this app in a Docker container:
- Claim a container: docker-sandbox init --use-pool
- Upload files, build backend/frontend
- Start server on port 5173
- Return the container ID and URL
- Release container when done"

### For Browser Testing
"Test this app with automated browser testing:
- Claim a container: docker-sandbox init --use-pool
- Run Playwright tests against the URL
- Capture screenshots as evidence
- Return test results
- Release container"

## Performance Tips

1. **Container Pool**: Use --use-pool for instant startup (0s vs 5-30s)
2. **Parallel Execution**: Launch multiple agents with different containers
3. **Cleanup**: Always kill containers when done to free resources
4. **Monitoring**: Check pool status regularly with docker ps

## Troubleshooting

**"No available containers in pool"**
- Pool exhausted (3 containers all claimed)
- Create new container: docker-sandbox init (without --use-pool)
- Wait for agents to release containers

**"Container timeout"**
- Docker containers have unlimited runtime
- Manual cleanup: docker-sandbox kill CONTAINER_ID

## See Also
- docker-sandbox skill: Direct container operations
- /root/flourisha/00_AI_Brain/documentation/PHASE2_DOCKER_MIGRATION_PLAN.md: Full Phase 2 details
