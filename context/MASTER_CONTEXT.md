# Flourisha System - Master Context

**Location:** `/root/flourisha/00_AI_Brain/`
**Purpose:** Quick system reference for all AI assistants

---

## System Identity

**Name:** Flourisha
**Role:** AI Chief of Staff
**Environment:** Personal AI Infrastructure (PAI) on Contabo VPS
**AI Engine:** Claude Code (multi-vendor capable)

---

## Quick Navigation

### AI Infrastructure
- **Skills:** `/root/flourisha/00_AI_Brain/skills/`
- **Documentation:** `/root/flourisha/00_AI_Brain/documentation/`
- **Scripts:** `/root/flourisha/00_AI_Brain/scripts/`
- **Context:** `/root/flourisha/00_AI_Brain/context/`

### Vendor Configs
- **Claude:** `/root/.claude/` (skills via symlink)
- **Gemini:** `/root/.gemini/` (future)

### Projects
- **Local AI Stack:** `/root/local-ai-packaged/`
- **ERPNext:** `/root/erpnext/`
- **Graphiti:** `/root/graphiti/`
- **MCP Servers:** `/root/mcp/`

---

## Key Services

### Docker Compose Stack (localai project)
- **n8n** - Workflow automation (https://n8n.leadingai.info)
- **Supabase** - Database/Auth (https://db.leadingai.info)
- **Neo4j** - Graph database (https://neo4j.leadingai.info)
- **Open WebUI** - AI chat interface (https://webui.leadingai.info)

### Monitoring & Management
- **Traefik** - Reverse proxy with Let's Encrypt
- **Portainer** - Docker management
- **Netdata** - System monitoring
- **Uptime Kuma** - Uptime monitoring

---

## Startup Procedures

**See:** `/root/flourisha/00_AI_Brain/documentation/startup/services.md`

**Quick Start:**
```bash
# Start all services
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py

# Start specific service
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --services neo4j
```

---

## Security

**See:** `/root/flourisha/00_AI_Brain/documentation/security/overview.md`

**Quick Security Check:**
```bash
# Firewall status
ufw status

# Running containers
docker ps

# System resources
htop
```

---

## MCP Servers

**See:** `/root/flourisha/00_AI_Brain/documentation/mcp-servers/overview.md`

**Installed Servers:**
- n8n-mcp
- graphiti
- filesystem
- [others in /root/.claude/.mcp.json]

---

## Google Drive Sync

**Flourisha Directory:**
- **Local:** `/root/flourisha/`
- **Google Drive:** `Flourisha_gDrive` shared drive
- **Obsidian:** `G:\Shared drives\Flourisha_gDrive` (Windows)

**Sync Command:**
```bash
flourisha-sync    # Bidirectional sync (one command for both ways)
```

**See:** `/root/flourisha/00_AI_Brain/documentation/sync/SYNC_GUIDE.md`

---

## Architecture

**Skills-as-Containers** (PAI v1.2.0):
- Skills in `/root/flourisha/00_AI_Brain/skills/`
- Each skill: SKILL.md + workflows/ + assets/ + examples/
- Progressive disclosure: metadata → instructions → resources
- Symlinked to vendor configs for compatibility

**Multi-Vendor Support:**
- Skills work with Claude, Gemini, Copilot
- Vendor-specific configs isolated
- Shared resources in AI Brain

---

## Contact Information

**User:** Greg Wasmuth
- Email: gwasmuth@gmail.com
- Wife: Joanna (jowasmuth@gmail.com)

**Social:**
- Website: https://www.gregwasmuth.com
- LinkedIn: https://www.linkedin.com/in/gregwasmuth/
- YouTube: https://www.youtube.com/@leadingai

---

## Server Details

**Provider:** Contabo VPS with IP 66.94.121.10 (never localhost)
**OS:** Ubuntu (Linux 6.8.0-87-generic)
**Location:** `/root/`
**Date Reference:** Check current date with `date` command


---

## Documentation

**Start here:** `/root/flourisha/00_AI_Brain/documentation/DOCUMENTATION_MAP.md`

### Quick Links
| Topic | Document |
|-------|----------|
| Document Processing | `documentation/services/DOCUMENT_PROCESSOR.md` |
| Knowledge Ingestion | `documentation/services/KNOWLEDGE_INGESTION.md` |
| Extraction Backends | `documentation/services/EXTRACTION_BACKENDS.md` |
| Database Schema | `documentation/database/DATABASE_SCHEMA.md` |
| Vector Store | `documentation/database/VECTOR_STORE.md` |
| Graph Store | `documentation/knowledge-stores/GRAPH_STORE.md` |
| Three-Store Overview | `documentation/knowledge-stores/OVERVIEW.md` |

### Other Documentation
- **Startup:** `documentation/startup/`
- **Security:** `documentation/security/`
- **Monitoring:** `documentation/monitoring/`
- **MCP Servers:** `documentation/mcp-servers/`
- **Infrastructure:** `documentation/infrastructure/`

---

**Last Updated:** 2025-12-06
**Version:** 1.1

**Recent Updates:**
- 2025-12-06: Added document extraction and knowledge ingestion documentation
- 2025-12-06: Reorganized documentation with DOCUMENTATION_MAP.md
- 2025-11-20: Simplified sync to single `flourisha-sync` command
- 2025-11-20: Added update-flourisha-brain skill for doc maintenance
