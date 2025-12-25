# Flourisha System Specification

**The Canonical Reference for Autonomous Development**

*Last Updated: 2025-12-24 | Version: 2.1*

---

# Executive Summary

Flourisha is a **Personal AI Infrastructure (PAI)** that helps people become more fully themselves through AI that recognizes, amplifies, and grows with them. Unlike traditional multi-tenant SaaS, Flourisha uses a **user-centric model** where your AI stays yours across organizations.

**Core Value Proposition:** A thinking friend that knows you deeply, reflects you back to yourself, and helps you see your own potential more clearly.

**Technical Foundation:**
- **Five Pillars:** CAPTURE → STORE → THINK → EXECUTE → GROW
- **Three-Store Architecture:** Vector (pgvector) + Graph (Neo4j) + Whole (Supabase)
- **Skills System:** 27+ AI skills orchestrated by Claude Code
- **Multi-Workspace:** User-centric, data-portable, cross-organization

---

# Quick Reference

## Status Indicators

| Status | Meaning |
|--------|---------|
| ✅ Working | Implemented, tested, in production |
| 🚧 In Progress | Actively being developed |
| 🔄 Planned | Designed but not built |
| ⚠️ Broken | Was working, needs fixing |

## Key Links

| Purpose | Document |
|---------|----------|
| **Agent routing** | [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md) - START HERE for autonomous work |
| Frontend features | [FRONTEND_FEATURE_REGISTRY.md](FRONTEND_FEATURE_REGISTRY.md) |
| All documentation | [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) |
| Autonomous tasks | [AUTONOMOUS_TASK_SPEC.md](AUTONOMOUS_TASK_SPEC.md) |
| Database schema | [database/DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) |
| Architecture decisions | [solution_architecture/ARCHITECTURE_DECISIONS.md](solution_architecture/ARCHITECTURE_DECISIONS.md) |

## For Autonomous Agents

**START WITH:** [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md) - your lean routing document (~400 tokens)

This SYSTEM_SPEC.md is the **reference document** for architecture and module context.
Load it on-demand when you need deeper understanding, not at session start.

**Single Source of Truth for Status:** ClickUp (not this document)

---

# Architecture

## Five Pillars Model

```
CAPTURE → STORE → THINK → EXECUTE → GROW
  │        │       │        │        │
Content  Store  Strategize  Act    Evolve
```

| Pillar | Purpose | Key Service |
|--------|---------|-------------|
| CAPTURE | Bring content in | `knowledge_ingestion_service.py` |
| STORE | Store & connect | Three-store architecture |
| THINK | Strategize & plan | Morning reports, OKRs |
| EXECUTE | Take action | Skills, agents |
| GROW | Improve system | Feedback loops |

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, TypeScript, Chakra UI, GSAP |
| **Mobile** | React Native (Expo) - Planned |
| **Backend** | FastAPI (Python), Claude Code |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Graph** | Neo4j + Graphiti |
| **Auth** | Firebase Authentication |
| **Voice** | ElevenLabs TTS, Deepgram STT |
| **Hosting** | Contabo VPS, Cloudflare |

## Infrastructure Services

| Service | Access | Purpose |
|---------|--------|---------|
| Supabase | Cloud | PostgreSQL + pgvector |
| Neo4j | `bolt://neo4j.leadingai.info:7687` | Graph database |
| Firebase | `flourisha-d959a` | Auth, Dynamic Links |
| Portainer | `https://portainer.leadingai.info` | Docker management |
| Netdata | `http://100.66.28.67:19999` | Monitoring |

---

# Feature Overview

**For task routing and status tracking, see:** [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md)

This section provides architectural context for each pillar. Status is tracked in ClickUp.

## Feature Counts by Pillar

| Pillar | Working | Planned | Total |
|--------|---------|---------|-------|
| CAPTURE | 8 | 5 | 13 |
| STORE | 6 | 3 | 9 |
| THINK | 5 | 4 | 9 |
| EXECUTE | 8 | 0 | 8 |
| GROW | 8 | 1 | 9 |
| PLATFORM | 3 | 8 | 11 |
| API | 0 | 6 | 6 |
| **Total** | **38** | **27** | **65** |

## Key Working Services

| Pillar | Key Services | Location |
|--------|--------------|----------|
| CAPTURE | YouTube, Documents, Gmail, Knowledge Pipeline | `services/` |
| STORE | Vector (pgvector), Graph (Neo4j), PARA | Supabase + Neo4j |
| THINK | Morning Report, OKRs, Energy, Daily Roadmap | `services/` + Skills |
| EXECUTE | Skills (27), Agents, ClickUp, Fabric | `~/.claude/skills/` |
| GROW | Feedback, Monitoring, Voice, Sandboxes | Various |

## API Build Status

The FastAPI backend (`/root/flourisha/00_AI_Brain/api/`) wraps existing services.

**Current focus:** Priority 1-2 tasks in [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md)

---

# Module: CAPTURE

**Purpose:** Bring content from anywhere into Flourisha's knowledge system.

## Architecture

```
Document → DocumentProcessor → ExtractionBackend → KnowledgeIngestionService
                                    │                        │
                              Claude (Primary)       Vector + Graph + Whole
                              Docling (Backup)
```

## Key Services

| Service | File | Purpose |
|---------|------|---------|
| Document Processor | `services/document_processor.py` | PDF, image extraction |
| Knowledge Ingestion | `services/knowledge_ingestion_service.py` | Route to three stores |
| YouTube Processor | `services/youtube_playlist_processor.py` | Playlist monitoring |
| Gmail Service | `services/gmail_service.py` | Email ingestion |

## Gmail Integration

Privacy-first: Only emails labeled `Flourisha/Unprocessed` are ingested.

| Setting | Value |
|---------|-------|
| Poll Interval | 5 minutes |
| Watch Label | `Flourisha/Unprocessed` |
| Done Label | `Flourisha/Processed` |
| Batch Size | 10 emails |

## Content Queue Worker

Background job processing from `processing_queue` table.

| Setting | Value |
|---------|-------|
| Poll Interval | 10 seconds |
| Max per Poll | 10 items |
| Job Types | YouTube, playlists, documents |

---

# Module: STORE

**Purpose:** Organize and store all knowledge for retrieval and connection.

## Three-Store Architecture

| Store | Technology | Purpose |
|-------|------------|---------|
| **Vector** | Supabase pgvector | Semantic search (1536-dim embeddings) |
| **Graph** | Neo4j + Graphiti | Entity relationships |
| **Whole** | Supabase raw | Original documents |

See [knowledge-stores/OVERVIEW.md](knowledge-stores/OVERVIEW.md) for full details.

## PARA Organization

```
/root/flourisha/
├── 00_AI_Brain/              # AI Infrastructure (this system)
├── 01f_Flourisha_Projects/   # PARA: Active projects
├── 02f_Flourisha_Areas/      # PARA: Ongoing responsibilities
├── 03f_Flourisha_Resources/  # PARA: Reference materials
└── 04f_Flourisha_Archives/   # PARA: Completed items
```

---

# Module: THINK

**Purpose:** AI Brain that understands you and helps you strategize.

## Morning Report

| Setting | Value |
|---------|-------|
| Delivery | 7:00 AM Pacific |
| Format | HTML via Mailgun |
| Sections | THE ONE THING, Yesterday, Today, OKRs, Energy |

## Energy Tracking

| Setting | Value |
|---------|-------|
| Method | Chrome extension + SMS |
| Interval | Every 90 minutes (8 AM - 6 PM) |
| Metrics | Energy 1-10, Focus quality |
| Storage | `energy_tracking` table |

---

# Module: EXECUTE

**Purpose:** Agents and skills that execute work on your behalf.

## Skills Architecture

Skills stored in Flourisha, symlinked for Claude Code:

| Location | Purpose |
|----------|---------|
| `/root/flourisha/00_AI_Brain/skills/` | Canonical (syncs to Drive) |
| `/root/.claude/skills/` | Symlink for Claude Code |

### Progressive Disclosure

| Tier | Content | Tokens | When Loaded |
|------|---------|--------|-------------|
| 1 | Frontmatter | ~100 | Startup (routing) |
| 2 | Instructions | ~2000 | When triggered |
| 3 | Resources | 500-2000 each | On-demand |

## Agent Types

| Type | Agents |
|------|--------|
| Research | perplexity-researcher, claude-researcher, gemini-researcher |
| Engineering | engineer, architect, pentester |
| Content | designer, writer (via Fabric) |

## Automation Schedule (Pacific Time)

| Time | Automation |
|------|------------|
| Every 15 min | Flourisha Sync |
| 2:00 AM | Full Backup |
| 6:00 AM | Security Check |
| 7:00 AM | Morning Report |
| Every 4 hours | PARA Analyzer |

---

# Module: GROW

**Purpose:** Continuous improvement through feedback loops.

## Feedback Loop Types

| Loop | Mechanism |
|------|-----------|
| Updated Documentation | Auto-capture learnings |
| New Skill Patterns | Skills from workflows |
| Learned Behaviors | Context Card updates |
| Enhanced Context | Entity extraction |

## Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Reliability | System uptime | 99.5%+ |
| Reliability | Morning report delivery | 95%+ |
| Performance | RAG query latency | < 2 seconds |
| Quality | Knowledge ingestion success | 95%+ |

---

# Module: PLATFORM

**Purpose:** Multi-workspace architecture, auth, and billing.

## Multi-Workspace Model

**Key Insight:** USER is primary entity, WORKSPACES are things they JOIN.

| Traditional | Flourisha |
|-------------|-----------|
| Tenant owns users | User joins workspaces |
| Data stays with org | Personal data is portable |
| One tenant per user | Multiple workspaces per user |

See [database/MULTI_WORKSPACE_SCHEMA.md](database/MULTI_WORKSPACE_SCHEMA.md) for full schema.

## Workspace Roles

| Role | Access | Billing |
|------|--------|---------|
| Owner | Full admin | Counts as seat |
| Admin | Manage members | Counts as seat |
| Member | Full access | Counts as seat |
| Guest | Limited, project-scoped | Free/reduced |
| External | Read-only | Free |

## Context Card Tiers

| Tier | Who Sees | Content |
|------|----------|---------|
| Public | Anyone | Name, headline, portfolio |
| Friends | Friends | Interests, hobbies, life context |
| Work | Colleagues | Skills, work style, projects |
| Workspace | Workspace members | Role, permissions, AI context |
| Private | Only you | Full personal context |

## Authentication

- **Provider:** Firebase Authentication (`flourisha-d959a`)
- **Methods:** Email/password, Google OAuth, Apple Sign-In
- **JWT:** Verified in FastAPI middleware
- **Deep Links:** Firebase Dynamic Links (planned)

## Billing & Monetization

See [MONETIZATION.md](MONETIZATION.md) for full details.

| Tier | Price | Credits |
|------|-------|---------|
| Starter | $20/month | 10,000 |
| Professional | $100/month | 100,000 |
| Enterprise | $200+/month | 500,000+ |

---

# Module: API

**Purpose:** FastAPI backend for production scaling.

## Two-Tier Execution Model

```
FastAPI (< 30 seconds)     Claude Code (> 30 seconds)
├── Intent routing          ├── Multi-step research
├── OAuth flows             ├── Document generation
├── RAG queries             ├── Long code sessions
└── Quick skill calls       └── Agentic workflows
```

## Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Document FastAPI endpoints | 🔄 Next |
| 2 | Build `/api/v1/execute` router | 🔄 Planned |
| 3 | Migrate skills to database | 🔄 Planned |
| 4 | OAuth integration layer | 🔄 Planned |
| 5 | Token refresh service | 🔄 Planned |
| 6 | Realtime job updates | 🔄 Planned |

See [solution_architecture/ARCHITECTURE_DECISIONS.md](solution_architecture/ARCHITECTURE_DECISIONS.md) for details.

---

# Module: INTEGRATIONS

**Purpose:** Connect external services.

## Integration Types

| Type | Use Case | Example |
|------|----------|---------|
| Direct API | REST API calls | ClickUp, Gmail, YouTube |
| MCP Server | Full bidirectional | Playwright |
| Skill Wrapper | Complex logic | research skill |

## Integration Status

| Service | Type | Status |
|---------|------|--------|
| ClickUp | Direct API | ✅ Working |
| Gmail | Direct API | ✅ Working |
| Google Calendar | Direct API | 🔄 Planned |
| Notion | MCP | 🔄 Planned |
| Slack | MCP | 🔄 Planned |
| Outlook | Direct API | 🔄 Planned |

---

# Autonomous Development

## Agent Entry Point

**Agents should start with:** [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md)

That document provides:
- File ownership map (prevents collisions)
- Build order with dependencies
- Priority tasks with exact file locations
- Session handoff protocol

## Harness Location

`/root/flourisha/00_AI_Brain/agents/clickup-autonomous/`

## ClickUp Reference

| Item | Value |
|------|-------|
| Space ID | `14700061` |
| List ID | `901112685055` |
| META Task | `868grh6hr` |

## Status Tracking

**Single Source of Truth:** ClickUp task status

Agents update ClickUp, not markdown documents. This prevents dual-tracking drift.

---

# MyRemoteLender Migration

**Status:** Phase 1 Complete (17 tables, 776 rows deployed)

## Overview

Migration of universal document management from Airtable + Make.com to Supabase + Knowledge Graph.

## Tables (mrl_ prefix)

| Table | Rows | Schema.org Type |
|-------|------|-----------------|
| `mrl_documents` | 39 | DigitalDocument |
| `mrl_loans` | 60 | LoanOrCredit |
| `mrl_properties` | 9 | RealEstateProperty |
| `mrl_companies` | 38 | Organization |

## Remaining Work

- [ ] Update ontology.py with MRL entities
- [ ] Map relationships to Graphiti edges
- [ ] Create Supabase → Neo4j pipeline
- [ ] Migrate Make.com scenarios

---

# Document Hierarchy

```
AGENT_WORK_INDEX.md          ← Agent entry point (~400 tokens)
    └── Points to subdocs as needed

SYSTEM_SPEC.md (this file)   ← Reference document (load on-demand)
    ├── FRONTEND_FEATURE_REGISTRY.md (UI specs)
    ├── DOCUMENTATION_MAP.md (index to all docs)
    │   ├── services/*.md
    │   ├── database/*.md
    │   └── knowledge-stores/*.md
    ├── AUTONOMOUS_TASK_SPEC.md (detailed task specs)
    └── plans/*.md (enhancement plans)

ClickUp                      ← Single source of truth for status
```

---

# Contact & Identity

| Field | Value |
|-------|-------|
| Name | Flourisha |
| Role | AI chief of staff |
| User | Greg Wasmuth |
| Location | San Diego, CA (Pacific Time) |
| Email | gwasmuth@gmail.com |

---

# Changelog (Last 10 Updates)

| Date | Change |
|------|--------|
| 2025-12-24 | v2.1 - Created AGENT_WORK_INDEX.md for tiered loading; ClickUp now single source of truth for status |
| 2025-12-24 | Removed duplicated Feature Registry (replaced with summary); updated harness prompts |
| 2025-12-24 | v2.0 - Complete restructure with proper H1 headings, Feature Registry, extracted schemas to subdocs |
| 2025-12-24 | Added credit system, assessments, affiliate program to MONETIZATION.md |
| 2025-12-24 | Extracted multi-workspace schema to database/MULTI_WORKSPACE_SCHEMA.md |
| 2025-12-24 | Added architectural decisions: FastAPI, two-tier execution |
| 2025-12-18 | Added Active Enhancement Plans section |
| 2025-12-18 | Synced with mindmap - added 14 missing items |
| 2025-12-18 | Added Chrome Extension features |
| 2025-12-18 | Added Firebase Dynamic Links |

---

*This is THE canonical system specification for architecture and context.*

*Autonomous agents: Start with [AGENT_WORK_INDEX.md](AGENT_WORK_INDEX.md) (~400 tokens)*

*For detailed frontend specs, see [FRONTEND_FEATURE_REGISTRY.md](FRONTEND_FEATURE_REGISTRY.md)*

*For document index, see [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)*
