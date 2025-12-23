# Phase 2: Docker Migration Plan

**Status**: DEFERRED (Phase 1 complete)
**Timeline**: After Phase 1 validation confirmed
**Objective**: Replace E2B with Docker for cost optimization while maintaining workflow patterns

---

## Executive Summary

Phase 2 will migrate agent sandbox execution from E2B (metered cost) to Docker (free on existing infrastructure) while **maintaining identical workflow patterns and agent prompt structures**.

### Why Phase 2 Matters

**Cost Impact**:
| Scenario | E2B Cost | Docker Cost | Savings |
|----------|----------|------------|---------|
| 10 × 1-hour sandboxes/month | $13-44 | $0 | 100% |
| 100 × 1-hour sandboxes/month | $130-440 | $0 | 100% |
| Production workload (100+ hrs/month) | $1,300-4,400 | $0 | 100% |

**No Workflow Changes**:
- Disler's patterns remain unchanged
- Agent prompts remain unchanged
- Success criteria and validation identical
- Only infrastructure substrate changes

---

## Architecture: E2B vs Docker

### E2B (Phase 1)
```
Agent Task
    ↓
E2B CLI (sbx commands)
    ↓
E2B Managed Service
    ↓
Public URLs
    ↓
Cloud Infrastructure (Metered)
```

**Pros**:
- ✅ No setup required
- ✅ Managed and reliable
- ✅ Public URL generation automatic
- ✅ Good for validation/testing

**Cons**:
- ❌ Per-hour billing
- ❌ 1-hour max timeout
- ❌ Account quotas
- ❌ Template restrictions

---

### Docker (Phase 2)
```
Agent Task
    ↓
Docker CLI (docker commands)
    ↓
Local Docker Daemon
    ↓
Internal Docker Network + Port Mapping
    ↓
Contabo Infrastructure (Existing)
```

**Pros**:
- ✅ Zero cost (use existing compute)
- ✅ Unlimited runtime
- ✅ Full control over templates
- ✅ Better for production
- ✅ Can migrate to K8s later

**Cons**:
- ❌ Requires setup
- ❌ Manual public URL exposure (via reverse proxy)
- ❌ Manual cleanup needed
- ❌ Resource management required

---

## Migration Strategy

### Phase 2a: Docker Foundation (Week 1)

**Objective**: Get Docker sandboxing working with same patterns as E2B

#### Step 1: Docker Sandbox Template

Create `/root/flourisha/01f_Flourisha_Projects/docker-sandbox-template/Dockerfile`:

```dockerfile
FROM ubuntu:22.04

# Install base requirements
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.pip \
    nodejs \
    npm \
    sqlite3 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
RUN mkdir -p /workspace
WORKDIR /workspace

# Install Python tools
RUN pip install --upgrade pip && pip install \
    fastapi \
    uvicorn \
    requests \
    python-dotenv

# Install Node tools
RUN npm install -g \
    vite \
    typescript

# Setup non-root user
RUN useradd -m -s /bin/bash coder
RUN chown -R coder:coder /workspace

EXPOSE 8000 5173 3000

CMD ["/bin/bash"]
```

**Why this works**:
- Matches E2B default template structure
- Same Python/Node versions as E2B defaults
- Can be enhanced to match disler's fullstack-vue-fastapi-node22

#### Step 2: Docker Sandbox Wrapper CLI

Create `/root/flourisha/scripts/docker-sandbox-cli.sh`:

```bash
#!/bin/bash
# Docker Sandbox CLI - mirrors E2B sbx commands

case "$1" in
    init)
        # docker-sandbox init --timeout 3600
        CONTAINER_ID=$(docker run -d \
            --name "flourisha-sandbox-$(date +%s)" \
            -v /workspace:/workspace \
            flourisha-sandbox:latest \
            sleep 3600)
        echo "Container created: $CONTAINER_ID"
        echo "$CONTAINER_ID"
        ;;

    exec)
        # docker-sandbox exec CONTAINER_ID "command"
        CONTAINER_ID=$2
        shift 2
        docker exec "$CONTAINER_ID" "$@"
        ;;

    ls)
        # docker-sandbox ls CONTAINER_ID /path
        CONTAINER_ID=$2
        PATH=$3
        docker exec "$CONTAINER_ID" ls -la "$PATH"
        ;;

    upload)
        # docker-sandbox upload CONTAINER_ID local_file remote_file
        CONTAINER_ID=$2
        LOCAL=$3
        REMOTE=$4
        docker cp "$LOCAL" "$CONTAINER_ID:$REMOTE"
        ;;

    download)
        # docker-sandbox download CONTAINER_ID remote_file local_file
        CONTAINER_ID=$2
        REMOTE=$3
        LOCAL=$4
        docker cp "$CONTAINER_ID:$REMOTE" "$LOCAL"
        ;;

    kill)
        # docker-sandbox kill CONTAINER_ID
        CONTAINER_ID=$2
        docker kill "$CONTAINER_ID"
        docker rm "$CONTAINER_ID"
        ;;

    get-host)
        # docker-sandbox get-host CONTAINER_ID
        # Returns localhost:PORT for local, or Tailscale IP:PORT for remote
        CONTAINER_ID=$2
        PORT=$3
        echo "http://localhost:$PORT"
        ;;
esac
```

#### Step 3: Update Flourisha Sandbox Skill

Modify `/root/.claude/skills/flourisha-sandbox/SKILL.md`:

```markdown
## Phase 1: E2B (Current)
\agent-sandboxes:init
\agent-sandboxes:exec

## Phase 2: Docker (Switch when Phase 1 validated)
\docker-sandbox:init
\docker-sandbox:exec
```

---

### Phase 2a.2: Browser Automation Testing (New - Discovered Gap)

**Objective**: Implement automated browser testing for Phase 4 validation

#### Step 1: Browser Test Infrastructure

Create Docker-based browser testing:

```dockerfile
FROM python:3.11-slim

# Install Playwright and browsers
RUN pip install playwright
RUN playwright install chromium

# Install test runner
RUN pip install pytest pytest-asyncio

EXPOSE 9223
WORKDIR /tests
```

#### Step 2: Browser Test Scripts

Create standardized test patterns:

```python
# tests/browser_test.py
import asyncio
from playwright.async_api import async_playwright

async def test_calculator():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate
        await page.goto("https://app-url")

        # Test calculation
        await page.click("text=5")
        await page.click("text=+")
        await page.click("text=3")
        await page.click("text==")

        # Verify
        result = await page.inner_text("#result")
        assert result == "8"

        # Screenshot evidence
        await page.screenshot(path="screenshot.png")

        await browser.close()
```

#### Step 3: Integration with Build Pipeline

Add browser tests to every Phase 4:

```
Phase 4: TEST
├── API validation
├── Browser tests (new)
├── Screenshots (evidence)
└── Regression reports
```

**Benefits in Docker**:
- Native Playwright support (no CDP complexity)
- Direct process access
- Faster test execution
- Built-in screenshot support
- Easier CI/CD integration

---

### Phase 2b: Agent Integration (Week 2)

Create `/root/.claude/skills/docker-sandbox-agent/SKILL.md`:

```markdown
---
name: docker-sandbox-agent
description: Execute Flourisha tasks in Docker containers with disler patterns. USE WHEN Phase 1 validation complete and cost optimization needed. Same workflows as E2B but with unlimited runtime and zero cost.
---
```

#### Step 2: Test Calculator Build with Docker

Run existing calculator spec (`very_easy_calculator.md`) with:
1. Docker container instead of E2B
2. Same Python/Node versions
3. Same success criteria
4. Verify identical output

**Expected Result**: All tests pass with Docker, identical to E2B

#### Step 3: Benchmark and Compare

| Metric | E2B | Docker | Winner |
|--------|-----|--------|--------|
| Startup time | ~30s | ~5s | Docker |
| Code execution time | Same | Same | Tie |
| Cost/hour | $0.13 | $0.00 | Docker |
| Memory isolation | Excellent | Good | E2B |
| Cleanup ease | Auto | Manual | E2B |

---

### Phase 2c: Production Hardening (Week 3)

#### Step 1: Resource Limits

Add to Docker daemon config:

```json
{
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
```

#### Step 2: Network Isolation

Create Docker network per sandbox:

```bash
docker network create sandbox-net-$(date +%s)
docker run --network sandbox-net-... flourisha-sandbox
```

#### Step 3: Automated Cleanup

Cron job to remove old containers:

```bash
# Remove containers older than 2 hours
0 * * * * docker ps -a --filter "created">2h -q | xargs docker rm -f
```

---

### Phase 2d: Reverse Proxy Integration (Week 4)

#### Step 1: Expose via Traefik

Add to docker-compose:

```yaml
services:
  sandbox-app:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.sandbox.rule=Host(`sandbox-CONTAINER_ID.leadingai.info`)"
      - "traefik.http.services.sandbox.loadbalancer.server.port=5173"
```

#### Step 2: Public URL Generation

Docker equivalent of E2B's `get-host`:

```bash
# E2B
sbx sandbox get-host [ID]
# Returns: https://i3ushomgcrnar3b8ihwa4.e2b.host

# Docker
docker-sandbox get-host [ID] 5173
# Returns: https://sandbox-CONTAINER_ID.leadingai.info
```

#### Step 3: Test Public Access

```bash
# Verify from outside
curl -H "Host: sandbox-CONTAINER_ID.leadingai.info" https://100.66.28.67
```

---

## Implementation Timeline

### Week 1: Docker Foundation
- [ ] Create Dockerfile template
- [ ] Build docker-sandbox-cli wrapper
- [ ] Verify container lifecycle management
- [ ] Test basic Python/Node execution

**Estimated effort**: 6 hours
**Blocker**: None

### Week 2: Integration & Testing
- [ ] Create docker-sandbox-agent skill
- [ ] Run calculator example with Docker
- [ ] Compare metrics with E2B
- [ ] Document differences/workarounds

**Estimated effort**: 8 hours
**Blocker**: Disler pattern validation

### Week 3: Hardening
- [ ] Add resource limits
- [ ] Implement network isolation
- [ ] Create cleanup automation
- [ ] Load test (50+ concurrent containers)

**Estimated effort**: 10 hours
**Blocker**: Infrastructure capacity testing

### Week 4: Production Readiness
- [ ] Integrate with Traefik reverse proxy
- [ ] Public URL generation
- [ ] Test external access
- [ ] Security audit

**Estimated effort**: 8 hours
**Blocker**: Traefik configuration

**Total Phase 2 Effort**: ~32 hours (4 weeks, part-time)

---

## Success Criteria

### Technical
- [ ] Calculator app builds identically in Docker as E2B
- [ ] All success criteria from disler pattern pass
- [ ] Public URLs accessible from outside
- [ ] Container cleanup automated
- [ ] Resource usage monitored
- [ ] Automated browser testing implemented (NEW)
- [ ] Screenshot evidence generated automatically (NEW)
- [ ] Playwright integration working in Docker (NEW)

### Operational
- [ ] Zero cost vs $0.13-0.44/hour with E2B
- [ ] Faster startup time (5s vs 30s)
- [ ] No runtime limits
- [ ] Same workflow patterns

### Documentation
- [ ] Docker sandbox skill documented
- [ ] Migration guide for agents
- [ ] Comparison table (E2B vs Docker)
- [ ] Troubleshooting guide

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Container resource exhaustion | High | Medium | Add limits, monitoring |
| Network isolation breakdown | High | Low | Security audit required |
| Docker daemon crash | High | Low | Systemd auto-restart |
| Public URL generation issues | Medium | Medium | Test Traefik thoroughly |
| Cleanup automation failure | Medium | Medium | Manual cleanup script |

---

## Rollback Plan

If Phase 2 issues arise:

1. **Keep E2B as fallback**: Don't deprecate immediately
2. **Gradual migration**: Test with non-critical tasks first
3. **Feature parity check**: Ensure Docker supports all needed operations
4. **Parallel running**: Run both systems during transition period

**Rollback command**:
```bash
# Switch skill back to E2B
cp ~/.claude/skills/flourisha-sandbox/SKILL.md.backup \
   ~/.claude/skills/flourisha-sandbox/SKILL.md
```

---

## Cost Savings Projection

### Current (Phase 1, E2B)
- 10 test runs/month × 1 hour = $1.30/month (at $0.13/hr)
- Agent development: 50 hours/month = $6.50/month
- **Total**: $7.80/month

### Future (Phase 2, Docker)
- Unlimited test runs = $0/month
- Agent development: 50 hours/month = $0/month
- **Total**: $0/month

### Annual Impact
- Current: $7.80 × 12 = **$93.60/year**
- Future: $0/year
- **Savings**: **$93.60/year** (100%)

*Note: As usage scales up, Docker savings become more significant.*

---

## Phase 2 Trigger

Phase 2 migration begins when:

1. ✅ Phase 1 E2B fully operational (DONE)
2. ✅ Disler patterns validated with E2B (IN PROGRESS)
3. ✅ Calculator app successfully built in E2B (NEXT)
4. [ ] Cost optimization approved by Greg
5. [ ] Docker infrastructure capacity verified

---

## Files to Create in Phase 2

```
/root/flourisha/
├── 01f_Flourisha_Projects/
│   └── docker-sandbox-template/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── README.md
├── scripts/
│   ├── docker-sandbox-cli.sh
│   ├── docker-sandbox-cleanup.sh
│   └── docker-sandbox-monitor.sh
└── 00_AI_Brain/
    └── documentation/
        ├── DOCKER_SANDBOX_GUIDE.md
        ├── DOCKER_VS_E2B_COMPARISON.md
        └── DOCKER_TROUBLESHOOTING.md

~/.claude/skills/
├── docker-sandbox/
│   └── SKILL.md
└── docker-sandbox-agent/
    └── SKILL.md
```

---

## Conclusion

Phase 2 Docker migration is a **straightforward infrastructure swap** that maintains all Flourisha workflow patterns while eliminating E2B costs. The 4-week implementation timeline provides low-risk validation before full production transition.

**Key Point**: No changes needed to disler's proven patterns—only the execution substrate changes from E2B to Docker.

