# [Flourisha AI] Documentation Map

**Complete index for all Flourisha AI Brain documentation.**

*Last Updated: 2025-12-19*

---

## Start Here

| Document | Purpose | When to Read |
|----------|---------|-----------------|
| [SYSTEM_SPEC.md](./SYSTEM_SPEC.md) | THE canonical reference | First read, system understanding |
| [FRONTEND_FEATURE_REGISTRY.md](./FRONTEND_FEATURE_REGISTRY.md) | All 30+ features detailed | Building/understanding features |
| This file | Complete documentation index | Finding specific docs |

---

## By Category

### System Overview
| Document | Description |
|----------|-------------|
| [SYSTEM_SPEC.md](./SYSTEM_SPEC.md) | Canonical system overview, Five Pillars, project list |
| [FRONTEND_FEATURE_REGISTRY.md](./FRONTEND_FEATURE_REGISTRY.md) | Complete feature inventory for frontend development |

### Guides
| Document | Description |
|----------|-------------|
| [guides/AUTONOMOUS_AGENT_GUIDE.md](./guides/AUTONOMOUS_AGENT_GUIDE.md) | **Getting started with ClickUp autonomous agent** |
| [guides/SETUP_AND_TESTING.md](./guides/SETUP_AND_TESTING.md) | Environment setup and testing procedures |
| [guides/USER_GUIDE.md](./guides/USER_GUIDE.md) | End-user documentation |
| [guides/FEATURE_IMPLEMENTATION_GUIDELINES.md](./guides/FEATURE_IMPLEMENTATION_GUIDELINES.md) | Guidelines for implementing new features |
| [guides/DOCUMENTATION_GUIDELINES.md](./guides/DOCUMENTATION_GUIDELINES.md) | Documentation standards and practices |
| [guides/DOCUMENTATION_PLACEMENT_QUICK_CARD.md](./guides/DOCUMENTATION_PLACEMENT_QUICK_CARD.md) | Quick reference for doc placement |
| [guides/QUICK_REFERENCE_PROJECTS.md](./guides/QUICK_REFERENCE_PROJECTS.md) | Project creation workflows and templates |
| [guides/SKILLS_QUICK_REFERENCE.md](./guides/SKILLS_QUICK_REFERENCE.md) | Quick reference for working with skills |

### Services (Pillar 1: INGEST)
| Document | Description |
|----------|-------------|
| [services/YOUTUBE_PLAYLIST_PROCESSOR.md](./services/YOUTUBE_PLAYLIST_PROCESSOR.md) | YouTube playlist processing |
| [services/TRANSCRIPT_SERVICE.md](./services/TRANSCRIPT_SERVICE.md) | YouTube transcripts via Tor + Whisper |
| [services/DOCUMENT_PROCESSOR.md](./services/DOCUMENT_PROCESSOR.md) | PDF, Word, Excel, image extraction |
| [services/KNOWLEDGE_INGESTION.md](./services/KNOWLEDGE_INGESTION.md) | Pipeline to all three stores |
| [services/EXTRACTION_BACKENDS.md](./services/EXTRACTION_BACKENDS.md) | Claude vs Docling backends |
| [services/gmail-integration.md](./services/gmail-integration.md) | Gmail integration |

### Services (Pillar 3: THINK)
| Document | Description |
|----------|-------------|
| [services/MORNING_REPORT.md](./services/MORNING_REPORT.md) | Daily 7 AM briefing email + 6 PM evening hook |
| [services/OKR_SYSTEM.md](./services/OKR_SYSTEM.md) | Quarterly OKR tracking |
| [services/ENERGY_TRACKING.md](./services/ENERGY_TRACKING.md) | 90-minute energy/focus tracking |

### Services (Pillar 4: EXECUTE)
| Document | Description |
|----------|-------------|
| [services/AGENT_FACTORY.md](./services/AGENT_FACTORY.md) | Temporal agent creation & A2A coordination |

### Database (Pillar 2: KNOW)
| Document | Description |
|----------|-------------|
| [database/DATABASE_SCHEMA.md](./database/DATABASE_SCHEMA.md) | Supabase tables, SQL files |
| [database/VECTOR_STORE.md](./database/VECTOR_STORE.md) | pgvector embeddings (1536 dim) |
| [database/SUPABASE_MIGRATION_GUIDE.md](./database/SUPABASE_MIGRATION_GUIDE.md) | Supabase migration procedures |

### Knowledge Stores (Pillar 2: KNOW)
| Document | Description |
|----------|-------------|
| [knowledge-stores/OVERVIEW.md](./knowledge-stores/OVERVIEW.md) | Three-store architecture overview |
| [knowledge-stores/GRAPH_STORE.md](./knowledge-stores/GRAPH_STORE.md) | Neo4j/Graphiti graph store |
| [knowledge-stores/IMPLEMENTATION_COMPLETE.md](./knowledge-stores/IMPLEMENTATION_COMPLETE.md) | Implementation status |

### Infrastructure (Pillar 5: GROW)
| Document | Description |
|----------|-------------|
| [infrastructure/TOR_PROXY_SETUP.md](./infrastructure/TOR_PROXY_SETUP.md) | Tor SOCKS5 proxy for YouTube |
| [infrastructure/DOCLING_SERVICE.md](./infrastructure/DOCLING_SERVICE.md) | Self-hosted OCR service |
| [infrastructure/SERVER_CONFIG.md](./infrastructure/SERVER_CONFIG.md) | Server configuration |
| [infrastructure/network-topology.md](./infrastructure/network-topology.md) | Network architecture |

### PAI System (Pillar 4: EXECUTE)
| Document | Description |
|----------|-------------|
| [pai-system/](./pai-system/) | Personal AI Infrastructure docs |
| [pai-system/FLOURISHA_CONTRACT.md](./pai-system/FLOURISHA_CONTRACT.md) | Core system contract and guarantees |
| [pai-system/SKILLS_UNIFICATION_STRATEGY.md](./pai-system/SKILLS_UNIFICATION_STRATEGY.md) | Skills system unification |
| [pai-system/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md](./pai-system/DISLER_PROMPT_ENGINEERING_PRINCIPLES.md) | Prompt engineering principles |
| Skills at `/root/.claude/skills/` | Skill definitions and workflows |

### MCP Servers
| Document | Description |
|----------|-------------|
| [mcp-servers/](./mcp-servers/) | Model Context Protocol servers |
| [mcp-servers/PLAYWRIGHT_MCP_SETUP.md](./mcp-servers/PLAYWRIGHT_MCP_SETUP.md) | Browser automation |

### A2A Protocol
| Document | Description |
|----------|-------------|
| [a2a/](./a2a/) | Agent-to-Agent protocol |
| [a2a/overview.md](./a2a/overview.md) | A2A protocol overview |
| [a2a/agent-cards.md](./a2a/agent-cards.md) | Agent card specification |

### Security
| Document | Description |
|----------|-------------|
| [security/](./security/) | Security guidelines and protocols |

### Monitoring
| Document | Description |
|----------|-------------|
| [monitoring/](./monitoring/) | System monitoring docs |

### Phase 2 (Docker Migration)
| Document | Description |
|----------|-------------|
| [phase2/PHASE2_DOCKER_MIGRATION_PLAN.md](./phase2/PHASE2_DOCKER_MIGRATION_PLAN.md) | Docker sandbox migration plan |

### Autonomous Development
| Document | Description |
|----------|-------------|
| [AUTONOMOUS_TASK_SPEC.md](./AUTONOMOUS_TASK_SPEC.md) | ClickUp agent harness task spec (75 tasks by Five Pillars) |
| `clickup-tasks` skill | Autonomous coding agent (use via skill system) |

### Archive
| Document | Description |
|----------|-------------|
| [archive/](./archive/) | Historical/superseded docs |
| [archive/FLOURISHA_AI_ARCHITECTURE.md](./archive/FLOURISHA_AI_ARCHITECTURE.md) | Original architecture (historical reference) |
| [archive/A2A_IMPLEMENTATION_COMPLETE.md](./archive/A2A_IMPLEMENTATION_COMPLETE.md) | A2A implementation completion record |
| [archive/IMPLEMENTATION_CONFIG.md](./archive/IMPLEMENTATION_CONFIG.md) | Old config decisions |
| [archive/IMPLEMENTATION_PLAN_COMPLIANCE.md](./archive/IMPLEMENTATION_PLAN_COMPLIANCE.md) | Old compliance tracking |
| [archive/phase1/](./archive/phase1/) | Phase 1 deployment docs |
| [deprecated/](./deprecated/) | Deprecated features/integrations |

---

## Directory Structure

```
/root/flourisha/00_AI_Brain/
├── QUICK_REFERENCE.md              # CLI commands
├── README.md                       # Basic intro
│
├── documentation/                   # All system docs
│   ├── README.md                  # Documentation index (with placement rules)
│   ├── DOCUMENTATION_MAP.md       # This file - complete navigation
│   ├── SYSTEM_SPEC.md             # THE canonical reference
│   ├── AUTONOMOUS_TASK_SPEC.md    # ClickUp harness spec (75 tasks)
│   ├── FRONTEND_FEATURE_REGISTRY.md # Feature inventory
│   │
│   ├── guides/                     # Setup and implementation guides
│   │   ├── AUTONOMOUS_AGENT_GUIDE.md  # Getting started with autonomous agent
│   │   ├── SETUP_AND_TESTING.md
│   │   ├── USER_GUIDE.md
│   │   ├── FEATURE_IMPLEMENTATION_GUIDELINES.md
│   │   ├── DOCUMENTATION_GUIDELINES.md
│   │   ├── DOCUMENTATION_PLACEMENT_QUICK_CARD.md
│   │   ├── QUICK_REFERENCE_PROJECTS.md
│   │   └── SKILLS_QUICK_REFERENCE.md
│   │
│   ├── services/                   # Service documentation
│   │   └── [12 service docs]
│   │
│   ├── database/                   # Database documentation
│   │   ├── DATABASE_SCHEMA.md
│   │   ├── VECTOR_STORE.md
│   │   └── SUPABASE_MIGRATION_GUIDE.md
│   │
│   ├── knowledge-stores/           # Three-store architecture
│   │   ├── OVERVIEW.md
│   │   ├── GRAPH_STORE.md
│   │   └── IMPLEMENTATION_COMPLETE.md
│   │
│   ├── infrastructure/             # Infrastructure docs
│   │   └── [8 infrastructure docs]
│   │
│   ├── pai-system/                 # PAI docs
│   │   ├── FLOURISHA_CONTRACT.md
│   │   ├── SKILLS_UNIFICATION_STRATEGY.md
│   │   └── DISLER_PROMPT_ENGINEERING_PRINCIPLES.md
│   │
│   ├── mcp-servers/                # MCP server docs
│   ├── a2a/                        # A2A protocol
│   ├── security/                   # Security docs
│   ├── monitoring/                 # Monitoring docs
│   ├── phase2/                     # Phase 2 Docker migration
│   │   └── PHASE2_DOCKER_MIGRATION_PLAN.md
│   ├── plans/                      # Enhancement plans (~/.claude/plans symlinks here)
│   │   ├── 2025-12-15-document-intelligence-pydantic-ai.md
│   │   ├── 2025-12-18-firebase-auth-documentation.md
│   │   └── 2025-12-19-ai-brain-root-cleanup.md
│   ├── archive/                    # Historical docs
│   │   ├── FLOURISHA_AI_ARCHITECTURE.md
│   │   ├── A2A_IMPLEMENTATION_COMPLETE.md
│   │   ├── IMPLEMENTATION_CONFIG.md
│   │   ├── IMPLEMENTATION_PLAN_COMPLIANCE.md
│   │   └── phase1/
│   ├── deprecated/                 # Deprecated docs
│   └── to-be-deleted/              # Staging for removal (verified duplicates)
│
├── skills/                         # PAI Skills
├── services/                       # Python services
├── scripts/                        # Automation scripts
├── config/                         # Configuration files
└── database/                       # SQL migrations
```

---

## Reading Order

### For System Understanding
1. [SYSTEM_SPEC.md](./SYSTEM_SPEC.md) - The canonical overview
2. [FRONTEND_FEATURE_REGISTRY.md](./FRONTEND_FEATURE_REGISTRY.md) - All features
3. Service-specific docs in `services/`

### For Building Features
1. [FRONTEND_FEATURE_REGISTRY.md](./FRONTEND_FEATURE_REGISTRY.md) - Find your feature
2. Service-specific docs in `services/`
3. [DATABASE_SCHEMA.md](./database/DATABASE_SCHEMA.md) - Database structure

### For Autonomous Development
1. [SYSTEM_SPEC.md](./SYSTEM_SPEC.md) - Context
2. [AUTONOMOUS_TASK_SPEC.md](./AUTONOMOUS_TASK_SPEC.md) - Tasks
3. `clickup-tasks` skill (invoke via skill system)

---

## Key Concepts

### Five Pillars Architecture
```
INGEST --> KNOW --> THINK --> EXECUTE --> GROW
```

| Pillar | Purpose | Key Components |
|--------|---------|----------------|
| **1. INGEST** | Content ingestion | YouTube, Documents, Gmail, Web |
| **2. KNOW** | Knowledge storage | Vector, Graph, Whole stores |
| **3. THINK** | Strategic command | Morning Report, OKRs, Energy |
| **4. EXECUTE** | Agentic operations | Skills, Agents, A2A Protocol |
| **5. GROW** | System evolution | Feedback, Monitoring, Improvement |

### Three-Store Knowledge System
| Store | Technology | Purpose |
|-------|------------|---------|
| Vector | Supabase pgvector | Semantic search (1536 dim) |
| Graph | Neo4j + Graphiti | Entity relationships |
| Whole | Supabase raw | Original documents |

---

## SQL Files

Database schemas at `/root/flourisha/00_AI_Brain/database/`:
- `01_content_intelligence_schema.sql` - Core tables
- `02_add_embeddings.sql` - Vector support
- `migrations/` - Migration files

---

*This is the complete documentation index. For the canonical overview, see [SYSTEM_SPEC.md](./SYSTEM_SPEC.md)*
