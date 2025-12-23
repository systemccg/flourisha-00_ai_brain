# Flourisha AI Brain - Documentation Index

**Location:** `/root/flourisha/00_AI_Brain/documentation/`
**Purpose:** Central system documentation for all AI assistants

---

## Quick Start

**New to the system?**
1. Read: [`DOCUMENTATION_MAP.md`](DOCUMENTATION_MAP.md) - **Start here** (master index)
2. Read: [`MASTER_CONTEXT.md`](../context/MASTER_CONTEXT.md) - System overview
3. Read: [`startup/services.md`](startup/services.md) - How to start services
4. Read: [`monitoring/overview.md`](monitoring/overview.md) - System monitoring

---

## Documentation Structure

### 📁 startup/
**Service startup and initialization**
- [`services.md`](startup/services.md) - Docker services startup guide
- `mcp-servers.md` - MCP server startup
- `verification.md` - Post-startup verification

### 📁 security/
**Security documentation and procedures**
- `overview.md` - Security posture overview
- [`scanning.md`](security/scanning.md) - Security scanning with Lynis
- [`SECURITY_CHECK_DAILY.md`](security/SECURITY_CHECK_DAILY.md) - Daily automated security checks
- `firewall.md` - UFW configuration
- `protocols.md` - Security protocols

### 📁 monitoring/
**System monitoring and observability**
- [`overview.md`](monitoring/overview.md) - Monitoring stack overview
- [`netdata.md`](monitoring/netdata.md) - Netdata usage
- `uptime-kuma.md` - Uptime monitoring
- `portainer.md` - Docker management

### 📁 phase2/
**Phase 2 Docker Sandbox Migration**
- [`PHASE2_STATUS.md`](phase2/PHASE2_STATUS.md) - Current migration status
- [`PHASE2_QUICK_START.md`](phase2/PHASE2_QUICK_START.md) - Quick start guide
- [`PHASE2_DOCKER_MIGRATION_PLAN.md`](phase2/PHASE2_DOCKER_MIGRATION_PLAN.md) - Full migration plan
- [`AGENT_SANDBOX_QUICK_START.md`](phase2/AGENT_SANDBOX_QUICK_START.md) - Using sandboxes

### 📁 mcp-servers/
**Model Context Protocol servers**
- [`PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md`](mcp-servers/PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md) - Playwright MCP setup
- `overview.md` - MCP architecture
- `server-list.md` - Installed servers
- `troubleshooting.md` - Common issues

### 📁 troubleshooting/
**Problem resolution**
- `docker.md` - Docker issues
- `networking.md` - Network problems
- `database.md` - Database issues
- `services.md` - Service-specific problems

### 📁 infrastructure/
**Infrastructure documentation**
- [`network-topology.md`](infrastructure/network-topology.md) - Network architecture (Tailscale + Docker)
- `server-specs.md` - Server specifications
- `backup-strategy.md` - Backup procedures
- `disaster-recovery.md` - DR procedures

### 📁 sync/
**Google Drive synchronization**
- [`SYNC_GUIDE.md`](sync/SYNC_GUIDE.md) - Simple sync guide
- [`SYNC_OPTIMIZATION_COMPLETE.md`](sync/SYNC_OPTIMIZATION_COMPLETE.md) - Optimization details
- [`SYNC_RECOVERY_AND_SAFETY.md`](sync/SYNC_RECOVERY_AND_SAFETY.md) - Recovery procedures

### 📁 services/ (New - 2025-12-06)
**AI Brain Service Documentation**
- [`DOCUMENT_PROCESSOR.md`](services/DOCUMENT_PROCESSOR.md) - Pluggable document extraction
- [`KNOWLEDGE_INGESTION.md`](services/KNOWLEDGE_INGESTION.md) - Pipeline to all stores
- [`EXTRACTION_BACKENDS.md`](services/EXTRACTION_BACKENDS.md) - Claude vs Docling backends

### 📁 database/ (New - 2025-12-06)
**Database Schema Documentation**
- [`DATABASE_SCHEMA.md`](database/DATABASE_SCHEMA.md) - All Supabase tables
- [`VECTOR_STORE.md`](database/VECTOR_STORE.md) - pgvector embeddings

### 📁 knowledge-stores/ (Renamed from knowledge-base)
**Three-Store Architecture Documentation**
- [`OVERVIEW.md`](knowledge-stores/OVERVIEW.md) - Vector + Graph + Whole overview
- [`GRAPH_STORE.md`](knowledge-stores/GRAPH_STORE.md) - Neo4j/Graphiti integration
- [`IMPLEMENTATION_COMPLETE.md`](knowledge-stores/IMPLEMENTATION_COMPLETE.md) - n8n RAG pattern
- [`workflows/`](knowledge-stores/workflows/) - Workflow documentation
- [`scripts/`](knowledge-stores/scripts/) - Utility scripts
- [`code/`](knowledge-stores/code/) - Code implementations

### 📁 deprecated/
**Archived Documentation**
- [`README.md`](deprecated/README.md) - Overview of deprecated items
- E2B Phase 1 integration docs (superseded by Phase 2 Docker)
- One-time integration projects (completed)
- Temporary solutions (archived for reference)

---

## Key Documents

### Canonical References (Start Here)
**[`SYSTEM_SPEC.md`](SYSTEM_SPEC.md)** - THE canonical system specification
- Five Pillars Architecture
- Complete feature status (61 features)
- Multi-Workspace Architecture
- Technology stack

**[`FRONTEND_FEATURE_REGISTRY.md`](FRONTEND_FEATURE_REGISTRY.md)** - Feature inventory
- All 30+ backend capabilities
- UI components needed
- Backend interfaces

### PAI System
**[`pai-system/FLOURISHA_CONTRACT.md`](pai-system/FLOURISHA_CONTRACT.md)** - Flourisha system contract
- Core guarantees (what always works)
- Configured functionality (needs setup)
- Health check commands

**[`pai-system/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md`](pai-system/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md)** - Disler's proven patterns
- 9 core principles for reliable agent tasks
- Specification templates and workflows

**[`pai-system/SKILLS_UNIFICATION_STRATEGY.md`](pai-system/SKILLS_UNIFICATION_STRATEGY.md)** - Skills organization
- Single source of truth for skills
- Symlink strategy
- Developer workflow

**Health Check:**
```bash
bun ~/.claude/hooks/self-test.ts
```

### Phase 2 Docker Migration
**[`phase2/PHASE2_DOCKER_MIGRATION_PLAN.md`](phase2/PHASE2_DOCKER_MIGRATION_PLAN.md)** - Phase 2 roadmap
- Docker vs E2B comparison
- 4-week implementation plan
- Cost savings projections

**Quick Start:** Read [`phase2/AGENT_SANDBOX_QUICK_START.md`](phase2/AGENT_SANDBOX_QUICK_START.md) for practical usage

### Archive (Historical)
**[`archive/A2A_IMPLEMENTATION_COMPLETE.md`](archive/A2A_IMPLEMENTATION_COMPLETE.md)** - A2A protocol integration
- Agent-to-agent interoperability
- Discovery registry

**[`archive/FLOURISHA_AI_ARCHITECTURE.md`](archive/FLOURISHA_AI_ARCHITECTURE.md)** - Original architecture doc
- Superseded by SYSTEM_SPEC.md

### System Startup
**[`startup/services.md`](startup/services.md)** - Complete service startup guide
- Start all services
- Start specific services
- Troubleshooting startup issues

### Security
**[`security/scanning.md`](security/scanning.md)** - Security scanning procedures
- Lynis security audit
- System hardening
- Vulnerability scanning

**[`security/SECURITY_CHECK_DAILY.md`](security/SECURITY_CHECK_DAILY.md)** - Daily automated security checks
- fail2ban integration
- UFW firewall monitoring
- Docker container health
- System updates tracking

### Monitoring
**[`monitoring/overview.md`](monitoring/overview.md)** - Monitoring tools overview
- Netdata system monitoring
- Uptime Kuma service monitoring
- Portainer container management

---

## Usage for AI Assistants

### Loading Context
1. **Tier 1 (Always):** [`../context/MASTER_CONTEXT.md`](../context/MASTER_CONTEXT.md) - Quick facts
2. **Tier 2 (When Needed):** Specific doc from this index
3. **Tier 3 (As Needed):** Deep dive into subsections

### Progressive Disclosure
- Load master context first (small, ~2000 tokens)
- Reference specific docs as needed
- Don't load everything at once

### Example Workflows

**User asks: "Start Neo4j"**
1. Read: [`../context/MASTER_CONTEXT.md`](../context/MASTER_CONTEXT.md) (know where scripts are)
2. Read: [`startup/services.md`](startup/services.md) (how to start services)
3. Execute: `python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --services neo4j`

**User asks: "Run security scan"**
1. Read: [`../context/MASTER_CONTEXT.md`](../context/MASTER_CONTEXT.md) (know security location)
2. Read: [`security/scanning.md`](security/scanning.md) (how to scan)
3. Execute: Security scanning procedures

---

## Documentation Placement Rules

**CRITICAL RULE (Non-Negotiable):**
> **ALL system-level documentation MUST go in `/root/flourisha/00_AI_Brain/documentation/` subdirectories**

### Quick Placement Guide

| Content | Category | Path |
|---------|----------|------|
| Phase 2 Docker migration | `phase2/` | `documentation/phase2/` |
| Server/infrastructure | `infrastructure/` | `documentation/infrastructure/` |
| MCP servers | `mcp-servers/` | `documentation/mcp-servers/` |
| Boot procedures | `startup/` | `documentation/startup/` |
| Security policies | `security/` | `documentation/security/` |
| Monitoring/alerts | `monitoring/` | `documentation/monitoring/` |
| Problem solving | `troubleshooting/` | `documentation/troubleshooting/` |
| PAI skills/agents | `pai-system/` | `documentation/pai-system/` |
| Services documentation | `services/` | `documentation/services/` |
| Database/schemas | `database/` | `documentation/database/` |
| Old/deprecated | `archive/` | `documentation/archive/` |

### ❌ WRONG Paths (Never create here):
- `/root/` (root directory)
- `/root/flourisha/` (Flourisha root)
- `/root/flourisha/00_AI_Brain/` (AI Brain root - only README.md and QUICK_REFERENCE.md allowed)
- `/root/flourisha/00_AI_Brain/documentation/` root (use subdirectories)

### ✅ Files Allowed at Documentation Root:
- `README.md` - This index file
- `DOCUMENTATION_MAP.md` - Master navigation index
- `SYSTEM_SPEC.md` - THE canonical system spec
- `FRONTEND_FEATURE_REGISTRY.md` - Feature inventory

### File Naming Convention
- Use `UPPER_CASE_WITH_UNDERSCORES.md`
- ✅ `PHASE2_STATUS.md`
- ❌ `phase2-status.md` (no hyphens)

---

## Documentation Principles

### Single Source of Truth
- System-level docs in subdirectories only
- Project-specific docs in project directories
- No duplication across locations

### Consistent Format
- Every doc: Overview → Prerequisites → Steps → Verification
- Code blocks are copy-pasteable
- Examples for common scenarios

### Maintenance
- Update when infrastructure changes
- Keep version history
- Review quarterly

---

## Syncing with Google Drive

**See:** [`sync/SYNC_GUIDE.md`](sync/SYNC_GUIDE.md) for complete sync documentation

This directory syncs with Google Drive:
- **Local:** `/root/flourisha/00_AI_Brain/documentation/`
- **Google Drive:** `Flourisha_gDrive/00_AI_Brain/documentation/`
- **Obsidian:** `G:\Shared drives\Flourisha_gDrive\00_AI_Brain\documentation\`

**Quick sync:**
```bash
flourisha-sync    # Bidirectional sync
```

**Edit in Obsidian:**
1. Open Obsidian on Windows
2. Navigate to `00_AI_Brain/documentation/`
3. Edit any .md file
4. Auto-syncs via Google Drive
5. Server sees updates automatically

---

## Quick Commands

```bash
# Navigate to docs
cd /root/flourisha/00_AI_Brain/documentation

# Search all docs
grep -r "search term" /root/flourisha/00_AI_Brain/documentation/

# List all docs
find /root/flourisha/00_AI_Brain/documentation -name "*.md"

# Sync to Google Drive
flourisha-sync
```

---

## Integration with Projects

Project-specific docs stay in projects:
- `/root/local-ai-packaged/CONTEXT.md` - n8n/Supabase
- `/root/mcp/n8n-mcp/README.md` - n8n MCP server
- `/root/graphiti/README.md` - Graphiti project

All reference this central documentation for system-level context.

---

**Last Updated:** 2025-12-18
**Maintainer:** Flourisha AI System

---

## Changelog

### 2025-12-18 - Documentation Cleanup
- Consolidated duplicate files (moved to `to-be-deleted/`)
- Moved historical docs to `archive/`
- Moved PAI system docs to `pai-system/`
- Merged documentation guidelines into this README
- Established SYSTEM_SPEC.md as THE canonical reference

### 2025-12-04 - PAI Architectural Improvements
- Centralized path resolution via `pai-paths.ts`
- Self-test health check system
- Protection validation system
- Pre-commit hook template
- Flourisha contract defined
