# Phase 2 - Docker Sandbox Migration

This directory contains documentation for Phase 2 of the Flourisha sandbox system: migrating from E2B cloud sandboxes to local Docker-based sandboxes.

## Files in This Category

- **[PHASE2_STATUS.md](./PHASE2_STATUS.md)** - Current migration status and progress tracking
- **[PHASE2_QUICK_START.md](./PHASE2_QUICK_START.md)** - Quick reference for getting started with Docker sandboxes
- **[PHASE2_DOCKER_MIGRATION_PLAN.md](./PHASE2_DOCKER_MIGRATION_PLAN.md)** - Complete 4-week implementation plan
- **[AGENT_SANDBOX_QUICK_START.md](./AGENT_SANDBOX_QUICK_START.md)** - How to use sandboxes with AI agents

## Quick Overview

**Goal:** Replace E2B cloud sandboxes with local Docker containers

**Key Benefits:**
- ✅ Unlimited runtime (vs 1-hour E2B timeout)
- ✅ Zero cost (vs $0.13-0.44/hour)
- ✅ Faster startup (~5s vs ~30s)
- ✅ Better testing (native Playwright support)

**Status:** [See PHASE2_STATUS.md](./PHASE2_STATUS.md)

## Getting Started

1. **First time?** Start with [PHASE2_QUICK_START.md](./PHASE2_QUICK_START.md)
2. **Want the full plan?** Read [PHASE2_DOCKER_MIGRATION_PLAN.md](./PHASE2_DOCKER_MIGRATION_PLAN.md)
3. **Using sandboxes?** See [AGENT_SANDBOX_QUICK_START.md](./AGENT_SANDBOX_QUICK_START.md)

## Implementation Timeline

| Phase | Timeline | Status |
|-------|----------|--------|
| 2a - Docker Foundation | Week 1 | See PHASE2_STATUS.md |
| 2b - Skills Integration | Week 2 | See PHASE2_STATUS.md |
| 2c - Traefik Integration | Week 3 | See PHASE2_STATUS.md |
| 2d - Resource Management | Week 3 | See PHASE2_STATUS.md |
| 2e - Browser Testing | Week 4 | See PHASE2_STATUS.md |

## Related Documentation

- **Infrastructure:** [../infrastructure/](../infrastructure/) - Server config, Traefik setup
- **MCP Servers:** [../mcp-servers/](../mcp-servers/) - Playwright MCP integration
- **Troubleshooting:** [../troubleshooting/](../troubleshooting/) - Common issues

## Commands

```bash
# View Phase 2 status
cat /root/flourisha/00_AI_Brain/documentation/phase2/PHASE2_STATUS.md

# Check Docker sandbox setup
docker images | grep flourisha-sandbox

# List active sandboxes
docker ps --filter "name=flourisha-qa"

# View Docker sandbox CLI help
/root/flourisha/00_AI_Brain/scripts/docker-sandbox-cli.sh
```

---

**Last Updated:** 2025-12-05
**Maintainer:** Flourisha AI System
