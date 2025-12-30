# Flourisha API Backend Summary

**Generated:** 2025-12-29 (Pacific Time)
**Location:** `/root/flourisha/00_AI_Brain/api/`
**Version:** 0.1.0

---

## Executive Summary

The Flourisha API is a comprehensive FastAPI backend that powers the Personal AI Infrastructure (PAI) system. It provides **43 router modules** covering knowledge management, content processing, productivity tools, multi-tenant workspace management, and third-party integrations.

### Quick Stats

| Metric | Count |
|--------|-------|
| Total Router Files | 43 |
| OpenAPI Tag Categories | 30 |
| Configured Env Vars | 50+ |
| External API Integrations | 15+ |

---

## Level 1: High-Level Architecture (5 Pillars)

The API follows the **Five Pillars** architecture:

| Pillar | Purpose | Key Routers |
|--------|---------|-------------|
| **INGEST** | Content ingestion | youtube, documents, gmail, transcript |
| **KNOW** | Knowledge storage | search, graph, ingestion |
| **THINK** | Strategic command | reports, okrs, energy, roadmap |
| **EXECUTE** | Agentic operations | skills, agents, fabric, a2a |
| **GROW** | System evolution | feedback, health_dashboard, memory |

---

## Level 2: Router Inventory by Category

### Content Ingestion (INGEST)
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| YouTube | `youtube.py` | 8 | Channel/playlist management |
| Documents | `documents.py` | 6 | PDF/image upload & extraction |
| Gmail | `gmail.py` | 10 | Email processing & sync |
| Transcript | `transcript.py` | 5 | YouTube transcript retrieval |

### Knowledge Storage (KNOW)
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Search | `search.py` | 3 | Unified semantic search |
| Graph | `graph.py` | 6 | Neo4j knowledge graph queries |
| Ingestion | `ingestion.py` | 4 | Three-store pipeline |
| PARA | `para.py` | 8 | File system navigation |

### Strategic Command (THINK)
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Reports | `reports.py` | 5 | Morning reports & briefings |
| OKRs | `okrs.py` | 12 | Objectives & Key Results |
| Energy | `energy.py` | 8 | Energy/focus tracking |
| Roadmap | `roadmap.py` | 4 | Daily planning |
| Context Card | `context_card.py` | 6 | Quick info cards |

### Agentic Operations (EXECUTE)
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Skills | `skills.py` | 8 | PAI skills registry |
| Skills DB | `skills_db.py` | 10 | Database-backed skills |
| Agents | `agents.py` | 12 | AI agent management |
| Fabric | `fabric.py` | 6 | Pattern execution |
| A2A | `a2a.py` | 8 | Agent-to-Agent protocol |
| ClickUp | `clickup.py` | 10 | Task management |

### System Evolution (GROW)
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Feedback | `feedback.py` | 8 | Extraction feedback |
| Health Dashboard | `health_dashboard.py` | 6 | System monitoring |
| Memory | `memory.py` | 10 | Mem0 persistent memory |
| Personality Profile | `personality_profile.py` | 6 | Contact profiles |

### Platform & Infrastructure
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Workspace | `workspace.py` | 15 | Multi-tenant workspaces |
| Invitations | `invitations.py` | 8 | Team invitations |
| Groups | `groups.py` | 10 | Permission groups |
| Profile | `profile.py` | 8 | User profiles |
| Billing | `billing.py` | 20+ | Stripe subscriptions |
| Integrations | `integrations.py` | 12 | Third-party OAuth |
| Nango | `nango.py` | 25+ | Unified OAuth (500+ APIs) |
| Hedra | `hedra.py` | 15 | Avatar generation |

### System Operations
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Crons | `crons.py` | 8 | Scheduled tasks |
| Migrations | `migrations.py` | 6 | Database migrations |
| Webhooks | `webhooks.py` | 6 | Incoming webhooks |
| Sync | `sync.py` | 4 | Google Drive sync |
| Voice | `voice.py` | 4 | ElevenLabs TTS |
| Queue | `queue.py` | 6 | Background jobs |

### Client Applications
| Router | File | Endpoints | Purpose |
|--------|------|-----------|---------|
| Chrome Extension | `chrome_extension.py` | 10 | Browser extension APIs |
| Mobile App | `mobile_app.py` | 20+ | React Native app APIs |

---

## Level 3: Technical Details

### Authentication System
- **Primary Auth:** Firebase JWT Bearer tokens
- **Admin Auth:** X-Admin-Secret / X-Cron-Secret headers
- **Webhook Auth:** HMAC-SHA256 signature verification
- **Multi-tenant:** Row-Level Security (RLS) via tenant_id

### Response Format
All endpoints return consistent `APIResponse`:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "duration_ms": 123,
    "timestamp": "2025-12-29T12:00:00-08:00"
  }
}
```

### Rate Limiting
- Standard: 1000 requests/hour
- Search: 100 requests/minute
- Webhooks: Unlimited (signature verified)

### Middleware Stack
1. `TimingMiddleware` - Request timing & IDs
2. `RateLimitMiddleware` - Per-user limits
3. `CORSMiddleware` - Cross-origin requests
4. Exception handlers - Consistent error format

### Database Backends
| Service | Technology | Purpose |
|---------|------------|---------|
| Primary DB | Supabase (PostgreSQL) | Structured data |
| Vector Store | pgvector (Supabase) | Semantic search |
| Graph DB | Neo4j + Graphiti | Entity relationships |
| Memory | Mem0 | Conversation memory |

---

## Level 4: File Structure

```
/root/flourisha/00_AI_Brain/api/
├── main.py              # FastAPI app entry point
├── config.py            # Settings from .env
├── models/              # Pydantic schemas
│   ├── response.py      # APIResponse, HealthStatus
│   ├── hedra.py         # Hedra models
│   ├── nango.py         # Nango models
│   └── ...
├── middleware/          # Request processing
│   ├── auth.py          # Firebase JWT auth
│   ├── timing.py        # Request timing
│   ├── rate_limit.py    # Rate limiting
│   └── exceptions.py    # Error handlers
├── routers/             # API endpoints (43 files)
│   ├── search.py
│   ├── youtube.py
│   ├── documents.py
│   └── ... (40 more)
├── services/            # Service wrappers
│   └── ...
├── scripts/             # Admin scripts
└── logs/                # Application logs
```

---

## Deployment Status

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI App | ✅ Ready | Run with `uv run uvicorn main:app` |
| Supabase | ✅ Connected | Via SUPABASE_URL |
| Neo4j | ✅ Connected | Via NEO4J_URI |
| Firebase Auth | ⚠️ Needs Config | FIREBASE_PROJECT_ID |
| Hedra | ⚠️ Needs Key | HEDRA_API_KEY |
| Nango | ⚠️ Needs Keys | NANGO_SECRET_KEY, NANGO_PUBLIC_KEY |
| Stripe | ⚠️ Test Mode | MCP_STRIPE_API_KEY (test key) |
| Mem0 | ⚠️ Optional | MEM0_API_KEY |

---

## Next Steps

1. **Configure missing API keys** - See `missing_api_dependencies.md`
2. **Run test suite** - See `testing_plan.md`
3. **Deploy to production** - Configure CORS, SSL, domains
4. **Build frontend** - Consume these APIs from React/Next.js

---

*Report generated by Flourisha AI Agent*
