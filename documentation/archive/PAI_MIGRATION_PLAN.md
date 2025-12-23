# Personal AI Infrastructure (PAI) Migration Plan
## Server: leadingai004.contaboserver.net

**Date**: 2025-11-14
**Goal**: Reorganize server to match Daniel Miessler's PAI architecture principles

---

## 🎯 Core Principles from Daniel's PAI

1. **Skills-as-Containers**: Group related services by domain/function
2. **Progressive Disclosure**: Hierarchical organization (don't load everything at once)
3. **Natural Language Routing**: Clear, intuitive naming for automatic discovery
4. **Platform Agnosticism**: No vendor lock-in, modular architecture
5. **Persistent Memory**: Plain-text configuration, version controlled
6. **Observability**: Clear documentation, logs, status tracking

---

## 📊 Current State Analysis

### Current Directory Structure (Scattered)
```
/root/
├── traefik/              # Reverse proxy
├── monitoring/           # Netdata, Uptime Kuma
├── local-ai-packaged/    # Supabase, Neo4j, Open WebUI, n8n
├── wordpress/            # Content management
├── portainer/            # Container management
├── filebrowser/          # File management
├── graphiti/             # Knowledge graph
├── backups/              # 12GB of backups
├── mcp/                  # MCP servers (849MB)
├── scripts/              # Various scripts
└── .claude/              # Claude Code state (not PAI-organized)
```

### Running Services (18 containers)
**Infrastructure**: traefik, netdata, uptime-kuma, portainer, filebrowser
**AI/ML Stack**: n8n, open-webui, supabase (6 containers), neo4j
**Applications**: wordpress, coolify (2 containers), mysql

### Problems with Current Structure
- ❌ Services scattered across flat directory structure
- ❌ No clear domain grouping (mixing infrastructure, AI, apps)
- ❌ Multiple docker-compose files in different locations
- ❌ Unclear which services depend on each other
- ❌ Documentation spread across multiple locations
- ❌ No clear "skill" organization

---

## 🏗️ Proposed PAI-Inspired Structure

### New Directory Architecture

```
/root/pai/                          # Personal AI Infrastructure root
│
├── skills/                         # Domain-based service organization
│   │
│   ├── CORE/                       # System identity & base infrastructure
│   │   ├── SKILL.md                # "Core infrastructure for AI platform"
│   │   ├── docker-compose.yml      # Traefik, Tailscale
│   │   ├── traefik/                # Reverse proxy configs
│   │   └── docs/
│   │       ├── ARCHITECTURE.md
│   │       └── NETWORK_MAP.md
│   │
│   ├── monitoring/                 # Observability & alerting
│   │   ├── SKILL.md                # "System health & service uptime monitoring"
│   │   ├── docker-compose.yml      # Netdata, Uptime Kuma, Lynis
│   │   ├── workflows/
│   │   │   ├── check-health.md
│   │   │   ├── send-alerts.md
│   │   │   └── security-audit.md
│   │   └── docs/
│   │       ├── NETDATA_GUIDE.md
│   │       ├── UPTIME_KUMA_GUIDE.md
│   │       └── LYNIS_AUDIT.md
│   │
│   ├── ai-automation/              # Workflow automation & AI orchestration
│   │   ├── SKILL.md                # "AI workflow automation and integration"
│   │   ├── docker-compose.yml      # n8n, Langfuse
│   │   ├── n8n/                    # Workflows, credentials
│   │   ├── workflows/
│   │   │   ├── create-workflow.md
│   │   │   ├── backup-workflows.md
│   │   │   └── deploy-workflow.md
│   │   └── docs/
│   │
│   ├── ai-knowledge/               # Knowledge management & graph databases
│   │   ├── SKILL.md                # "Knowledge graph and semantic storage"
│   │   ├── docker-compose.yml      # Neo4j, Graphiti, Supabase
│   │   ├── neo4j/                  # Graph database
│   │   ├── supabase/               # Relational + vector DB
│   │   ├── graphiti/               # Knowledge graph tools
│   │   ├── workflows/
│   │   │   ├── query-knowledge.md
│   │   │   ├── import-data.md
│   │   │   └── backup-graphs.md
│   │   └── docs/
│   │
│   ├── ai-inference/               # AI model serving & chat interfaces
│   │   ├── SKILL.md                # "AI model hosting and chat interfaces"
│   │   ├── docker-compose.yml      # Open WebUI, Ollama (future)
│   │   ├── open-webui/             # Chat interface
│   │   ├── models/                 # Model storage
│   │   ├── workflows/
│   │   │   ├── chat-session.md
│   │   │   ├── manage-models.md
│   │   │   └── api-integration.md
│   │   └── docs/
│   │
│   ├── content-creation/           # Content management & publishing
│   │   ├── SKILL.md                # "Content creation and publishing"
│   │   ├── docker-compose.yml      # WordPress
│   │   ├── wordpress/              # CMS
│   │   ├── workflows/
│   │   │   ├── write-post.md
│   │   │   ├── publish-content.md
│   │   │   └── backup-site.md
│   │   └── docs/
│   │
│   └── management/                 # Infrastructure management tools
│       ├── SKILL.md                # "Infrastructure and container management"
│       ├── docker-compose.yml      # Portainer, Filebrowser, Coolify
│       ├── portainer/              # Container UI
│       ├── filebrowser/            # File management
│       ├── workflows/
│       │   ├── deploy-service.md
│       │   ├── manage-containers.md
│       │   └── file-operations.md
│       └── docs/
│
├── agents/                         # Orchestration scripts
│   ├── backup-agent.sh             # Automated backups
│   ├── health-check-agent.sh       # Health monitoring
│   ├── deploy-agent.sh             # Service deployment
│   └── security-agent.sh           # Security scans
│
├── backups/                        # Centralized backup storage
│   ├── daily/
│   ├── weekly/
│   └── configs/
│
├── shared/                         # Shared resources across skills
│   ├── networks/                   # Docker network definitions
│   ├── volumes/                    # Shared volume configs
│   └── secrets/                    # Encrypted secrets (git-crypt)
│
├── docs/                           # Central documentation
│   ├── ARCHITECTURE.md             # System architecture
│   ├── SERVICES_MAP.md             # All services catalog
│   ├── ACCESS_GUIDE.md             # URLs & credentials
│   ├── SETUP.md                    # Initial setup guide
│   └── MIGRATION_LOG.md            # This migration record
│
├── .env                            # Environment variables
├── docker-compose.yml              # Master compose (references all skills)
└── README.md                       # Quick start guide
```

---

## 🔄 Migration Mapping

### What Moves Where

| Current Location | New Location | Reason |
|-----------------|--------------|---------|
| `/root/traefik/` | `/root/pai/skills/CORE/traefik/` | Core infrastructure |
| `/root/monitoring/` | `/root/pai/skills/monitoring/` | Already well-organized |
| `/root/local-ai-packaged/supabase/` | `/root/pai/skills/ai-knowledge/supabase/` | Knowledge storage |
| `/root/local-ai-packaged/neo4j/` | `/root/pai/skills/ai-knowledge/neo4j/` | Knowledge graph |
| `/root/graphiti/` | `/root/pai/skills/ai-knowledge/graphiti/` | Knowledge tools |
| `/root/local-ai-packaged/n8n/` | `/root/pai/skills/ai-automation/n8n/` | Workflow automation |
| `/root/local-ai-packaged/open-webui/` | `/root/pai/skills/ai-inference/open-webui/` | Chat interface |
| `/root/wordpress/` | `/root/pai/skills/content-creation/wordpress/` | Content management |
| `/root/portainer/` | `/root/pai/skills/management/portainer/` | Container mgmt |
| `/root/filebrowser/` | `/root/pai/skills/management/filebrowser/` | File mgmt |
| `/root/backups/` | `/root/pai/backups/` | Centralized backups |
| `/root/scripts/` | `/root/pai/agents/` | Automation scripts |
| `/root/mcp/` | `/root/pai/shared/mcp/` | Shared MCP servers |
| Documentation files | `/root/pai/docs/` | Central documentation |

### What Gets Consolidated

**Multi-service directories** like `/root/local-ai-packaged/` get **split by domain**:
- Supabase, Neo4j, Graphiti → `ai-knowledge/`
- n8n, Langfuse → `ai-automation/`
- Open WebUI → `ai-inference/`

---

## 📝 Skill Definition Template

Each skill will have a `SKILL.md` following this pattern:

```markdown
# [Skill Name] - Skill Definition

**Domain**: [Infrastructure/AI/Management]
**Purpose**: [One-line description]
**Services**: [List of Docker services]

## Progressive Disclosure

### Tier 1: Metadata (Always Loaded)
- Skill name and domain
- Primary services included
- Key capabilities

### Tier 2: Instructions (On-Demand)
- How to deploy services
- Configuration options
- Common workflows

### Tier 3: Resources (As-Needed)
- Detailed documentation
- Troubleshooting guides
- API references

## Natural Language Triggers

This skill activates when you ask about:
- [List of trigger phrases]

## Dependencies

- Required: [Other skills]
- Optional: [Enhancement skills]

## Quick Start

\`\`\`bash
cd /root/pai/skills/[skill-name]
docker compose up -d
\`\`\`
```

---

## 🚀 Migration Phases

### Phase 1: Structure Setup (No Service Disruption)
**Duration**: 30 minutes
**Downtime**: None

1. Create new `/root/pai/` directory structure
2. Create all `skills/` subdirectories
3. Create SKILL.md for each domain
4. Copy (don't move) docker-compose files to new locations
5. Update docker-compose files with new paths (but don't deploy yet)
6. Create master docker-compose.yml that references all skills

**Commands**:
```bash
# Create structure
mkdir -p /root/pai/skills/{CORE,monitoring,ai-automation,ai-knowledge,ai-inference,content-creation,management}
mkdir -p /root/pai/{agents,backups,shared,docs}

# Copy documentation
cp /root/SERVER_STATUS_SUMMARY.md /root/pai/docs/
cp /root/NEW_SERVER_ACCESS_URLS.md /root/pai/docs/ACCESS_GUIDE.md
```

### Phase 2: Service-by-Service Migration (With Testing)
**Duration**: 1-2 hours
**Downtime**: Rolling (one service at a time)

**Order of Migration** (least critical → most critical):

1. ✅ **Coolify** (least used) → Remove or migrate to management/
2. ✅ **WordPress** → content-creation/
3. ✅ **Filebrowser** → management/
4. ✅ **Portainer** → management/
5. ✅ **Monitoring** (Netdata, Uptime Kuma) → monitoring/
6. ✅ **Neo4j** → ai-knowledge/
7. ✅ **Graphiti** → ai-knowledge/
8. ✅ **Open WebUI** → ai-inference/
9. ✅ **n8n** → ai-automation/
10. ✅ **Supabase** (6 containers) → ai-knowledge/
11. ✅ **Traefik** (last - most critical) → CORE/

**For each service**:
```bash
# 1. Stop service
cd /root/[old-location]
docker compose down

# 2. Move files
mv /root/[old-location] /root/pai/skills/[domain]/[service]

# 3. Update paths in docker-compose.yml
# 4. Test start
cd /root/pai/skills/[domain]
docker compose up -d

# 5. Verify in Uptime Kuma
# 6. Check Traefik routing
```

### Phase 3: Documentation & Automation
**Duration**: 1 hour
**Downtime**: None

1. Create workflow markdown files for each skill
2. Update all documentation with new paths
3. Create agent scripts for common tasks
4. Set up master docker-compose.yml
5. Test full stack restart
6. Update backup scripts with new paths
7. Update monitoring alerts with new paths

### Phase 4: Cleanup & Validation
**Duration**: 30 minutes
**Downtime**: None

1. Remove old empty directories
2. Clean up old docker-compose files
3. Verify all services accessible
4. Run Lynis security audit on new structure
5. Update firewall rules if needed
6. Create rollback snapshot

---

## 🎯 Benefits of PAI Structure

### Before (Current)
- 7 scattered docker-compose files
- No clear domain organization
- Mixed concerns (AI + infrastructure + apps)
- Documentation scattered in 15+ files
- Unclear service dependencies

### After (PAI-Organized)
- ✅ Clear skill-based domains (7 skills)
- ✅ Progressive disclosure (don't load everything)
- ✅ Natural language routing (clear naming)
- ✅ Self-contained workflows per domain
- ✅ Centralized documentation
- ✅ Easier to add new services (just add to appropriate skill)
- ✅ Clearer backup strategy (per-skill backups)
- ✅ Better security (skill-level isolation)

---

## ⚠️ Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Service downtime during migration | Migrate one service at a time, test each |
| Traefik routing breaks | Update labels before moving, test routing |
| Volume data loss | Copy first, verify, then move |
| Path references in configs | Find/replace all paths, test thoroughly |
| User confusion with new structure | Create comprehensive README and guides |
| Rollback if issues | Keep old structure until fully validated |

---

## 📋 Pre-Migration Checklist

- [ ] Full server backup (all volumes and configs)
- [ ] Document all current service URLs
- [ ] Export all current credentials
- [ ] Test Uptime Kuma is monitoring all services
- [ ] Verify Netdata email alerts working
- [ ] Create rollback plan
- [ ] Schedule maintenance window (or do rolling updates)
- [ ] Notify any users of potential brief downtime

---

## 🔄 Rollback Plan

If migration causes critical issues:

1. **Immediate**: Restart services from old locations
```bash
cd /root/[old-location]
docker compose up -d
```

2. **Full Rollback**: Restore from backup
```bash
# Restore from pre-migration backup
/root/pai/backups/restore-from-backup.sh [backup-date]
```

3. **Partial Rollback**: Keep migrated services, revert problematic ones
```bash
# Move problematic service back
mv /root/pai/skills/[domain]/[service] /root/[old-location]
```

---

## 📊 Success Metrics

After migration is complete:

- ✅ All 18 containers running and healthy
- ✅ All public URLs accessible (checked by Uptime Kuma)
- ✅ All management tools accessible via Tailscale
- ✅ Traefik routing working correctly
- ✅ Email alerts still functioning
- ✅ All documentation updated with new paths
- ✅ Master docker-compose.yml can restart all services
- ✅ Backup scripts updated and tested
- ✅ Security score maintained or improved

---

## 🎓 Post-Migration Enhancements

Once PAI structure is in place, you can:

1. **Add Claude Code Skills**: Create workflow markdown files for common tasks
2. **Set up Agents**: Automate backup, health checks, deployments
3. **Implement MCP Servers**: For service integration
4. **Create Status Pages**: Public dashboard using PAI structure
5. **Add More Services**: Easily slot into appropriate skill domain
6. **Version Control**: Git repo for /root/pai/ (exclude data volumes)

---

## 📞 Support During Migration

**Pre-migration review**: Review this plan, adjust as needed
**During migration**: Step-by-step execution with testing
**Post-migration**: Validation and documentation updates

---

## 🚦 Ready to Proceed?

**Recommendation**: Start with **Phase 1** (structure setup) to see the organization without any service disruption. This gives you a preview of the new structure and lets you validate the concept before moving services.

**Estimated Total Time**: 3-4 hours for complete migration
**Recommended Approach**: Rolling migration (one service at a time)
**Best Time**: During low-usage hours or maintenance window

---

**Questions to Confirm:**

1. Do you want to proceed with Phase 1 (structure setup) immediately?
2. Should we migrate all services, or keep some in current locations?
3. Any specific services you're concerned about moving?
4. Do you want to add any additional skills/domains to the structure?
5. Should we set up version control (git) for the PAI directory?
