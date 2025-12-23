# [Flourisha AI] Frontend Feature Registry

**Purpose:** Complete inventory of all Flourisha backend capabilities for frontend development, organized by the Five Pillars architecture.

**Last Updated:** 2025-12-17

**Canonical Reference:** For system overview, see [SYSTEM_SPEC.md](./SYSTEM_SPEC.md)

**How to Use:** Hand this document to a frontend developer. Each feature includes what it does, how to call it, what data it produces, and what UI components are needed.

---

## Table of Contents (Linkable)

- [Flourisha AI Frontend Feature Registry](#flourisha-ai-frontend-feature-registry)
  - [The Five Pillars of Flourisha](#the-five-pillars-of-flourisha)
- [0. PLATFORM ARCHITECTURE](#0-platform-architecture-platform)
  - [0.1 Multi-Workspace System](#01-multi-workspace-system)
  - [0.2 User Identity & Authentication](#02-user-identity--authentication)
  - [0.3 Workspace Management](#03-workspace-management)
  - [0.4 Groups & Permissions](#04-groups--permissions)
  - [0.5 Context Cards](#05-context-cards)
  - [0.6 Invitation & Onboarding](#06-invitation--onboarding)
  - [0.7 Integrations Hub](#07-integrations-hub)
- [1. CONTENT INGESTION](#1-content-ingestion-ingest)
  - [1.1 YouTube Playlist Processor](#11-youtube-playlist-processor)
  - [1.2 YouTube Multi-Channel Manager](#12-youtube-multi-channel-manager)
  - [1.3 Transcript Service](#13-transcript-service)
  - [1.4 Document Processor](#14-document-processor)
  - [1.5 Knowledge Ingestion Pipeline](#15-knowledge-ingestion-pipeline)
  - [1.6 Gmail Integration](#16-gmail-integration)
  - [1.7 Flourisha Sync (Google Drive)](#17-flourisha-sync-google-drive)
- [2. KNOWLEDGE HUB](#2-knowledge-hub-know)
  - [2.1 Three-Store Architecture Overview](#21-three-store-architecture-overview)
  - [2.2 Vector Store (Semantic Search)](#22-vector-store-semantic-search)
  - [2.3 Graph Store (Entity Relationships)](#23-graph-store-entity-relationships)
  - [2.4 PARA Organization](#24-para-organization)
  - [2.5 Memory System](#25-memory-system)
- [3. STRATEGIC COMMAND](#3-strategic-command-think)
  - [3.1 Context Card System](#31-context-card-system)
  - [3.2 Morning Report](#32-morning-report)
  - [3.3 OKR System](#33-okr-system)
  - [3.4 Energy Tracking](#34-energy-tracking)
  - [3.5 Daily Roadmap](#35-daily-roadmap)
- [4. AGENTIC OPERATIONS](#4-agentic-operations-execute)
  - [4.1 Skills System](#41-skills-system)
  - [4.2 Specialized Agents](#42-specialized-agents)
  - [4.3 A2A Protocol (Agent-to-Agent)](#43-a2a-protocol-agent-to-agent)
  - [4.4 Hook System](#44-hook-system)
  - [4.5 Command System](#45-command-system)
  - [4.6 Fabric Prompts](#46-fabric-prompts)
- [5. SYSTEM EVOLUTION](#5-system-evolution-grow)
  - [5.1 Extraction Feedback System](#51-extraction-feedback-system)
  - [5.2 Extraction Backends](#52-extraction-backends)
  - [5.3 Voice System](#53-voice-system)
  - [5.4 ClickUp Integration](#54-clickup-integration)
  - [5.5 System Monitoring (Netdata)](#55-system-monitoring-netdata)
  - [5.6 Uptime Monitoring (Uptime Kuma)](#56-uptime-monitoring-uptime-kuma)
  - [5.7 Playwright MCP (Browser Automation)](#57-playwright-mcp-browser-automation)
  - [5.8 Database Layer](#58-database-layer)
- [6. Frontend Architecture](#6-frontend-architecture)
  - [6.1 Recommended Tech Stack](#61-recommended-tech-stack)
  - [6.2 API Layer Needs](#62-api-layer-needs)
  - [6.3 Priority Implementation Order](#63-priority-implementation-order)
  - [Feature Request Template](#feature-request-template)

---

## The Five Pillars of Flourisha

```
┌─────────────────────────────────────────────────────────────────┐
│                         FLOURISHA AI                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INGEST ──► 2. KNOW ──► 3. THINK ──► 4. EXECUTE ──► 5. GROW │
│                                                                  │
│  Content       Knowledge    Strategic    Agentic      System     │
│  Ingestion     Hub          Command      Operations   Evolution  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

**0. PLATFORM ARCHITECTURE [platform]**
- [0.1 Multi-Workspace System](#01-multi-workspace-system)
- [0.2 User Identity & Authentication](#02-user-identity--authentication)
- [0.3 Workspace Management](#03-workspace-management)
- [0.4 Groups & Permissions](#04-groups--permissions)
- [0.5 Context Cards](#05-context-cards)
- [0.6 Invitation & Onboarding](#06-invitation--onboarding)
- [0.7 Integrations Hub](#07-integrations-hub)

**1. CONTENT INGESTION [ingest]**
- [1.1 YouTube Playlist Processor](#11-youtube-playlist-processor)
- [1.2 YouTube Multi-Channel Manager](#12-youtube-multi-channel-manager)
- [1.3 Transcript Service](#13-transcript-service)
- [1.4 Document Processor](#14-document-processor)
- [1.5 Knowledge Ingestion Pipeline](#15-knowledge-ingestion-pipeline)
- [1.6 Gmail Integration](#16-gmail-integration)
- [1.7 Flourisha Sync (Google Drive)](#17-flourisha-sync-google-drive)

**2. KNOWLEDGE HUB [know]**
- [2.1 Three-Store Architecture Overview](#21-three-store-architecture-overview)
- [2.2 Vector Store (Semantic Search)](#22-vector-store-semantic-search)
- [2.3 Graph Store (Entity Relationships)](#23-graph-store-entity-relationships)
- [2.4 PARA Organization](#24-para-organization)
- [2.5 Memory System](#25-memory-system)

**3. STRATEGIC COMMAND [think]**
- [3.1 Context Card System](#31-context-card-system)
- [3.2 Morning Report](#32-morning-report)
- [3.3 OKR System](#33-okr-system)
- [3.4 Energy Tracking](#34-energy-tracking)
- [3.5 Daily Roadmap](#35-daily-roadmap)

**4. AGENTIC OPERATIONS [execute]**
- [4.1 Skills System](#41-skills-system)
- [4.2 Specialized Agents](#42-specialized-agents)
- [4.3 A2A Protocol (Agent-to-Agent)](#43-a2a-protocol-agent-to-agent)
- [4.4 Hook System](#44-hook-system)
- [4.5 Command System](#45-command-system)
- [4.6 Fabric Prompts](#46-fabric-prompts)

**5. SYSTEM EVOLUTION [grow]**
- [5.1 Extraction Feedback System](#51-extraction-feedback-system)
- [5.2 Extraction Backends](#52-extraction-backends)
- [5.3 Voice System](#53-voice-system)
- [5.4 ClickUp Integration](#54-clickup-integration)
- [5.5 System Monitoring (Netdata)](#55-system-monitoring-netdata)
- [5.6 Uptime Monitoring (Uptime Kuma)](#56-uptime-monitoring-uptime-kuma)
- [5.7 Playwright MCP (Browser Automation)](#57-playwright-mcp-browser-automation)
- [5.8 Database Layer](#58-database-layer)

**6. Frontend Architecture**
- [6.1 Recommended Tech Stack](#61-recommended-tech-stack)
- [6.2 API Layer Needs](#62-api-layer-needs)
- [6.3 Priority Implementation Order](#63-priority-implementation-order)

---

# 0. PLATFORM ARCHITECTURE [platform]

> **Purpose:** User-centric multi-workspace foundation that enables Personal AI portability across organizations.
>
> **Key Principle:** USER is the primary entity. Workspaces are things users JOIN. Personal AI travels with the user.
>
> **Canonical Reference:** [SYSTEM_SPEC.md - Multi-Workspace Architecture](./SYSTEM_SPEC.md#multi-workspace-architecture)

---

## 0.1 Multi-Workspace System

**What it does:** Enables users to maintain a personal workspace (free forever) while joining multiple organization workspaces. Personal data stays with user; work products stay with workspace.

**Data model:**
- `users` - Primary entity with global identity
- `workspaces` - Personal (1 per user) or Team (shared)
- `workspace_memberships` - Junction table with role

**API routes needed:**
```
GET    /api/workspaces                    - List user's workspaces
POST   /api/workspaces                    - Create new workspace
GET    /api/workspaces/:id                - Get workspace details
PUT    /api/workspaces/:id                - Update workspace settings
DELETE /api/workspaces/:id                - Delete workspace (owner only)
POST   /api/workspaces/:id/switch         - Switch active workspace context
```

**UI components needed:**
- [ ] Workspace switcher (dropdown in header)
- [ ] Workspace list/grid view
- [ ] Create workspace modal
- [ ] Workspace settings page
- [ ] Personal vs Team workspace badge

**Status:** 🔄 Planned (Phase 2)

---

## 0.2 User Identity & Authentication

**What it does:** Global user identity that persists across workspaces. Single sign-on, portable profile, personal workspace auto-created on signup.

**Authentication flow:**
1. User signs up → Personal workspace auto-created
2. User logs in → Returns to last active workspace
3. User can switch workspaces without re-auth

**Data model:**
- `users.email` - Primary identifier
- `users.personal_workspace_id` - Always exists
- `users.subscription_tier` - Personal tier (free/pro)

**API routes needed:**
```
POST   /api/auth/signup                   - Create account + personal workspace
POST   /api/auth/login                    - Authenticate
POST   /api/auth/logout                   - End session
GET    /api/auth/me                       - Current user + workspaces
PUT    /api/auth/me                       - Update profile
POST   /api/auth/password                 - Change password
```

**UI components needed:**
- [ ] Sign up form (email + password)
- [ ] Login form
- [ ] Profile settings page
- [ ] Account deletion flow
- [ ] OAuth providers (Google, GitHub) - optional

**Integration:** Supabase Auth recommended

**Status:** 🔄 Planned (Phase 2)

---

## 0.3 Workspace Management

**What it does:** Admin controls for workspace owners and admins - billing, settings, member management, group configuration.

**Workspace types:**
- `personal` - Single user, free forever, can't invite others
- `team` - Multiple users, billing per seat

**API routes needed:**
```
GET    /api/workspaces/:id/settings       - Get all settings
PUT    /api/workspaces/:id/settings       - Update settings
GET    /api/workspaces/:id/billing        - Billing info
POST   /api/workspaces/:id/billing        - Update billing
GET    /api/workspaces/:id/usage          - Usage stats
POST   /api/workspaces/:id/export         - Export workspace data
```

**Workspace settings structure:**
```json
{
  "general": {
    "name": "Acme Corp",
    "slug": "acme-corp",
    "icon": "url",
    "description": "..."
  },
  "members": {
    "allow_member_invites": true,
    "default_role": "member",
    "require_approval": false
  },
  "ai": {
    "ai_enabled": true,
    "ai_model_preference": "claude-sonnet",
    "ai_memory_enabled": true
  },
  "security": {
    "require_2fa": false,
    "sso_enabled": false,
    "allowed_domains": ["acme.com"]
  }
}
```

**UI components needed:**
- [ ] Workspace settings tabs (General, Members, AI, Security, Billing)
- [ ] Billing dashboard with seat count
- [ ] Usage analytics (storage, API calls)
- [ ] Danger zone (transfer ownership, delete)

**Status:** 🔄 Planned (Phase 3)

---

## 0.4 Groups & Permissions

**What it does:** Workspace-scoped groups with hierarchy support for fine-grained access control. Groups enable Teams → Departments → Divisions structure via `parent_group_id`.

**Key concepts:**
- Groups are workspace-scoped (not global)
- `parent_group_id` enables flexible hierarchy
- `hierarchy_type` suggests structure: team, department, division
- Users can be in multiple groups (access = UNION)

**API routes needed:**
```
GET    /api/workspaces/:id/groups         - List groups (with hierarchy)
POST   /api/workspaces/:id/groups         - Create group
GET    /api/groups/:id                    - Get group details
PUT    /api/groups/:id                    - Update group
DELETE /api/groups/:id                    - Delete group
GET    /api/groups/:id/members            - List group members
POST   /api/groups/:id/members            - Add member to group
DELETE /api/groups/:id/members/:userId    - Remove member
GET    /api/groups/:id/descendants        - Get child groups (reporting)
```

**UI components needed:**
- [ ] Group tree view (hierarchical)
- [ ] Group list view (flat)
- [ ] Create/edit group modal
- [ ] Group member management
- [ ] Group permission settings
- [ ] Drag-drop hierarchy editor
- [ ] Group AI context editor

**Status:** 🔄 Planned (Phase 3)

---

## 0.5 Context Cards

**What it does:** Tiered visibility profiles that control what information workspaces see about a user. Five tiers: public, friends, work, workspace-specific, private.

**Tiers:**
| Tier | Visibility | Contains |
|------|------------|----------|
| `public` | Anyone | Name, headline, public portfolio |
| `friends` | Personal connections | Interests, hobbies, personal AI preferences |
| `work` | Professional connections | Skills, experience, work style |
| `workspace:ID` | Specific workspace only | Role, work products, org-specific AI context |
| `private` | Only user | Personal notes, private AI learnings |

**API routes needed:**
```
GET    /api/context-card                  - Get own context card (all tiers)
PUT    /api/context-card/:tier            - Update specific tier
GET    /api/users/:id/context-card        - Get another user's card (respects visibility)
POST   /api/context-card/preview          - Preview card as seen by target
```

**UI components needed:**
- [ ] Context card editor (tabbed by tier)
- [ ] Context card preview (as seen by others)
- [ ] Visibility controls per field
- [ ] Import from LinkedIn (optional)
- [ ] Export context card (PDF)
- [ ] Context card viewer (for viewing others)

**Status:** 🔄 Planned (Phase 4)

---

## 0.6 Invitation & Onboarding

**What it does:** Invitation flow for adding users to workspaces. Supports email invites, link invites, and role assignment.

**Invitation types:**
- Email invite (specific person)
- Link invite (anyone with link)
- Domain invite (auto-join for @company.com)

**Invitation states:**
- `pending` - Sent, awaiting response
- `accepted` - User joined
- `declined` - User declined
- `expired` - Past expiration date

**API routes needed:**
```
POST   /api/workspaces/:id/invitations    - Create invitation
GET    /api/workspaces/:id/invitations    - List pending invitations
DELETE /api/invitations/:id               - Revoke invitation
POST   /api/invitations/:token/accept     - Accept invitation
POST   /api/invitations/:token/decline    - Decline invitation
GET    /api/invitations/:token            - Get invitation details (for preview)
```

**Onboarding flow:**
1. User receives invite (email or link)
2. User views workspace preview (name, member count, description)
3. User accepts → creates account (if new) or joins (if existing)
4. User selects context card tier to share with workspace
5. User added to default groups
6. User sees workspace dashboard

**UI components needed:**
- [ ] Invite member modal (email input, role select)
- [ ] Pending invitations list
- [ ] Invitation preview page (public, for recipients)
- [ ] Accept/decline flow
- [ ] Context card tier selector (during onboarding)
- [ ] Welcome wizard (after joining)

**Status:** 🔄 Planned (Phase 6)

---

## 0.7 Integrations Hub

**What it does:** Centralized management for all external integrations (email, calendar, storage, ERP, CRM). Uses the best approach for each: MCP, Direct API, or Skill wrappers.

**Integration Types:**
| Type | When to Use | Examples |
|------|-------------|----------|
| **MCP Server** | AI-native tools, dynamic addition | Gmail, Slack, Playwright |
| **Direct API** | Performance-critical, complex auth | YouTube, Neo4j, Supabase |
| **Skill Wrapper** | Multi-step workflows | ClickUp, Google Drive sync |

**Integration Categories:**

| Category | Integrations | Type | Status |
|----------|--------------|------|--------|
| **Email** | Gmail, Outlook | MCP | Gmail ✅, Outlook 🔄 |
| **Calendar** | Google Calendar, Outlook | Direct/MCP | GCal ✅, Outlook 🔄 |
| **Storage** | Google Drive, OneDrive | Skill/MCP | GDrive ✅, Others 🔄 |
| **Project Mgmt** | ClickUp, Asana, Linear | Skill | ClickUp ✅, Others 🔄 |
| **Communication** | Slack, Discord, Teams | MCP | All 🔄 |
| **CRM** | Salesforce, HubSpot | MCP/API | All 🔄 |
| **ERP** | QuickBooks, Xero, Odoo | MCP/API | All 🔄 |
| **Database** | Neo4j, Supabase | Direct API | All ✅ |
| **Content** | YouTube | Direct API | ✅ Working |

**API routes needed:**
```
GET    /api/integrations                  - List all integrations + status
GET    /api/integrations/:id              - Get integration details
POST   /api/integrations/:id/connect      - Initiate OAuth flow
POST   /api/integrations/:id/disconnect   - Revoke access
GET    /api/integrations/:id/status       - Check connection health
POST   /api/integrations/:id/sync         - Trigger manual sync
GET    /api/integrations/:id/logs         - Recent sync logs
```

**UI components needed:**
- [ ] Integration catalog (browse available)
- [ ] Connected integrations list
- [ ] OAuth connect flow
- [ ] Integration settings per-connection
- [ ] Sync status indicators
- [ ] Sync logs viewer
- [ ] Add custom integration wizard (advanced)

**Per-integration settings:**
```json
{
  "gmail": {
    "connected": true,
    "connected_at": "2025-12-15",
    "sync_labels": ["INBOX", "IMPORTANT"],
    "auto_ingest": true,
    "last_sync": "2025-12-18T10:30:00Z",
    "sync_frequency": "15m"
  }
}
```

**Status:** Gmail ✅ Working, Others 🔄 Planned

**Canonical Reference:** [SYSTEM_SPEC.md - Integrations Architecture](./SYSTEM_SPEC.md#integrations-architecture)

---

# 1. CONTENT INGESTION [ingest]

> **Purpose:** Bring content from everywhere into Flourisha's knowledge system.
>
> **Sources:** Files (PDF, Spreadsheets, Text, Images, Video), Inboxes (Email, iPostal), Voice (Limitless), Videos (YouTube), Web pages (RSS)
>
> **Process:** Ingest → Validate → Synthesize → Store

---

## 1.1 YouTube Playlist Processor

**What it does:** Processes YouTube videos from playlists, extracts transcripts via Tor proxy, generates AI summaries with Opus 4.5, routes outputs to PARA folders based on content type.

**Backend interface:**
```bash
cd /root/flourisha/00_AI_Brain

# List all templates
python3 services/youtube_playlist_processor.py templates

# Preview playlist (shows template mapping)
python3 services/youtube_playlist_processor.py preview "flourisha-enhancements"

# Process videos
python3 services/youtube_playlist_processor.py process "playlist-name" --limit 5

# Dry run (no files created)
python3 services/youtube_playlist_processor.py process "playlist-name" --limit 2 --dry-run
```

**Data produced:**

| Content Type | Output Location |
|--------------|-----------------|
| Flourisha enhancements | `01f_Flourisha_Projects/flourisha-enhancements/youtube-ideas/*.md` |
| Health insights | `02f_Flourisha_Areas/health/youtube-insights/*.md` |
| Business insights | `02f_Flourisha_Areas/business/youtube-insights/*.md` |
| Finance insights | `02f_Flourisha_Areas/finance/youtube-insights/*.md` |
| Personal development | `02f_Flourisha_Areas/personal-growth/youtube-insights/*.md` |
| Music production | `03f_Flourisha_Resources/music-production/youtube-notes/*.md` |
| Transcripts | Same folder, `*_transcript.md` suffix |

**Output format per video:**
- Summary markdown with YAML frontmatter (title, video_id, creator, dates)
- Creator name + clickable link to their YouTube channel
- Video description with all original links preserved
- Link to full transcript file
- AI analysis based on template (implementation plans, protocol updates, etc.)

**UI components needed:**
- [ ] Playlist selector dropdown (grouped by channel)
- [ ] Template preview (show which template will be used)
- [ ] Process button with limit input field
- [ ] Progress indicator during processing
- [ ] Results viewer with markdown rendering
- [ ] "Discuss this idea" button (opens chat about video)
- [ ] Priority queue (filter by High/Medium/Low)
- [ ] Category tabs (Flourisha, Health, Business, etc.)
- [ ] Transcript viewer modal with search

**Configuration:** `/root/flourisha/00_AI_Brain/config/youtube_playlist_templates.json`

**Documentation:** [services/YOUTUBE_PLAYLIST_PROCESSOR.md](./services/YOUTUBE_PLAYLIST_PROCESSOR.md)

---

## 1.2 YouTube Multi-Channel Manager

**What it does:** Manages OAuth tokens for multiple YouTube channels (brand accounts). Switch between channels to access different playlists.

**Backend interface:**
```bash
# List authenticated channels
python3 services/youtube_channel_manager.py list

# Show playlists for a channel
python3 services/youtube_channel_manager.py playlists "CoCreators Group"

# Set default channel
python3 services/youtube_channel_manager.py default "Wazzy"

# Authenticate new channel (OAuth Playground flow)
python3 services/youtube_channel_manager.py auth
```

**Data produced:**
- Channel registry: `/root/flourisha/00_AI_Brain/credentials/youtube_channels.json`
- Tokens per channel: `/root/flourisha/00_AI_Brain/credentials/youtube_tokens/`

**Authenticated channels:**

| Channel | Playlists | Default |
|---------|-----------|---------|
| CoCreators Group | 30 | Yes |
| Wazzy | 83 | No |

**UI components needed:**
- [ ] Channel switcher dropdown with icons
- [ ] "Add channel" button (triggers OAuth flow)
- [ ] Channel status indicator (valid/expired token)
- [ ] Playlists list per channel with video counts

---

## 1.3 Transcript Service

**What it does:** Two-tier YouTube transcript extraction: YouTube API via Tor proxy (2-5 sec) with Whisper fallback for videos without captions (1-15 min).

**Backend interface:**
```bash
# Get transcript for a video
python3 services/transcript_service.py "VIDEO_ID"

# Force Whisper transcription
python3 services/transcript_service.py "VIDEO_ID" --whisper-only
```

**Data produced:**
- `TranscriptResult` with: success, transcript text, source (YOUTUBE_API/WHISPER), language, metadata

**UI components needed:**
- [ ] Transcript viewer panel
- [ ] Copy transcript button
- [ ] Searchable transcript text
- [ ] Source indicator (API vs Whisper)
- [ ] Language selector

**Documentation:** [services/TRANSCRIPT_SERVICE.md](./services/TRANSCRIPT_SERVICE.md)

---

## 1.4 Document Processor

**What it does:** Extracts text, entities, and structured data from PDFs, Word docs, Excel files, and images using pluggable backends (Claude primary, Docling fallback).

**Backend interface:**
```python
from services.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_file("/path/to/document.pdf", use_new_backend=True, extract_entities=True)

# Result contains: raw_text, markdown, entities, relationships, confidence, validation_errors
```

**Supported formats:** PDF, DOCX, DOC, TXT, MD, XLSX, XLS, CSV, PNG, JPG, JPEG, GIF, WEBP

**Entity types extracted:** medication, person, date, condition, vital_sign, procedure, instruction, allergy

**Data produced:**
- Extracted text stored in Supabase
- Embeddings in pgvector (1536 dimensions)
- Entities and relationships in Neo4j graph

**UI components needed:**
- [ ] Document upload dropzone (drag & drop)
- [ ] Processing progress indicator with stages
- [ ] Extracted content preview (markdown rendered)
- [ ] Entity list with type badges
- [ ] Relationship visualization (graph view)
- [ ] Confidence indicator per extraction
- [ ] Validation warnings display
- [ ] Backend selector (Claude vs Docling)

**Critical warning:** Docling may miss styled content boxes. Always use Claude backend for medical documents.

**Documentation:** [services/DOCUMENT_PROCESSOR.md](./services/DOCUMENT_PROCESSOR.md)

---

## 1.5 Knowledge Ingestion Pipeline

**What it does:** Orchestrates document ingestion to three stores (Vector, Graph, Whole) for unified search and entity relationship tracking.

**Backend interface:**
```python
from services.knowledge_ingestion_service import get_ingestion_service

service = get_ingestion_service(tenant_id="default")
result = service.ingest_document(file_path, document_type="pdf")

# Query across all stores
results = service.query_knowledge(
    query="what medications interact with X?",
    search_vector=True,
    search_graph=True,
    limit=10
)
```

**Data produced:**
- Document ID (SHA256 hash for deduplication)
- Chunks (1000 chars with 200 overlap)
- Vector embeddings in Supabase pgvector
- Entity graph in Neo4j
- Raw document in Supabase

**UI components needed:**
- [ ] Ingestion status dashboard
- [ ] Store health indicators (Vector/Graph/Whole)
- [ ] Unified search interface
- [ ] Results with source attribution
- [ ] Deduplication indicator

**Documentation:** [services/KNOWLEDGE_INGESTION.md](./services/KNOWLEDGE_INGESTION.md)

---

## 1.6 Gmail Integration

**What it does:** Privacy-first selective email ingestion. Only emails tagged with "Flourisha/Unprocessed" are synced.

**Backend interface:**
```
POST /api/gmail/auth          # Start OAuth
GET  /api/gmail/callback      # OAuth callback
POST /api/gmail/labels/create # Create Flourisha label
POST /api/gmail/sync          # Sync tagged emails
```

**Status:** Planning phase (not yet deployed)

**UI components needed:**
- [ ] Gmail connect button (OAuth)
- [ ] Label management UI
- [ ] Sync trigger button
- [ ] Synced email list
- [ ] Email content viewer

**Documentation:** [services/gmail-integration.md](./services/gmail-integration.md)

---

## 1.7 Flourisha Sync (Google Drive)

**What it does:** Bidirectional sync between server `/root/flourisha/` and Google Drive for Obsidian access on Windows.

**Backend interface:**
```bash
# Primary sync command
flourisha-sync

# Dry run (preview changes)
flourisha-sync --dry-run

# Force resync (after conflicts)
flourisha-sync --resync
```

**Excluded from sync:**
- Dependencies: `node_modules/`, `__pycache__/`
- VCS: `.git/`
- Build: `dist/`, `build/`, `.next/`
- IDEs: `.vscode/`, `.idea/`
- Large files: `*.db`, `>10MB`

**Conflict handling:** Creates `.conflict-1/.conflict-2` files for manual review

**UI components needed:**
- [ ] Sync status indicator (idle/syncing/error)
- [ ] Last sync timestamp
- [ ] Manual sync button
- [ ] Conflict resolution UI
- [ ] Excluded files list

**Documentation:** [sync/SYNC_GUIDE.md](./sync/SYNC_GUIDE.md)

---

# 2. KNOWLEDGE HUB [know]

> **Purpose:** Organize and store all knowledge for retrieval and connection.
>
> **Structure:** PARA (Projects, Areas, Resources, Archives)
>
> **Three Parallel Storage Systems:** Vector Store (semantic search), Graph Store (relationships), Whole Document Store (complete context)
>
> **Access:** Obsidian on Google Drive Desktop + Memory via oMem

---

## 2.1 Three-Store Architecture Overview

**What it does:** Unified knowledge management using three complementary storage systems that work together.

| Store | Technology | Purpose | Query Type |
|-------|------------|---------|------------|
| **Vector** | Supabase pgvector | Semantic search | "Find similar content" |
| **Graph** | Neo4j + Graphiti | Entity relationships | "How is X connected to Y?" |
| **Whole** | Supabase raw | Original documents | "Show me the source" |

**UI components needed:**
- [ ] Unified search bar (queries all stores)
- [ ] Store toggle filters
- [ ] Results merged and ranked
- [ ] Source attribution per result
- [ ] Visualized as networked nodes

**Documentation:** [knowledge-stores/OVERVIEW.md](./knowledge-stores/OVERVIEW.md)

---

## 2.2 Vector Store (Semantic Search)

**What it does:** Semantic similarity search using OpenAI embeddings (text-embedding-3-small, 1536 dimensions).

**Backend interface:**
```python
from services.embeddings_service import EmbeddingsService

service = EmbeddingsService()
results = service.search_similar_content(
    query="project management best practices",
    tenant_id="default",
    threshold=0.7,
    limit=10
)
```

**SQL function:** `search_content_by_embedding(query_embedding, tenant_id, threshold, match_count)`

**Data produced:**
- Results with: id, title, content_type, summary, tags, similarity score (0-1)

**UI components needed:**
- [ ] Semantic search input
- [ ] Similarity threshold slider (0.5-0.9)
- [ ] Results ranked by similarity score
- [ ] Score visualization (progress bar)
- [ ] Content preview cards

**Documentation:** [database/VECTOR_STORE.md](./database/VECTOR_STORE.md)

---

## 2.3 Graph Store (Entity Relationships)

**What it does:** Knowledge graph showing how entities are connected. Query relationships like "what medications interact with X?" or "who works on this project?"

**Backend interface:**
```python
from services.knowledge_graph_service import get_knowledge_graph

kg = get_knowledge_graph()

# Add content
kg.add_episode(
    content_id="doc_abc123",
    tenant_id="default",
    title="Medical Summary",
    content="Full text...",
    summary="Summary text"
)

# Search
results = kg.search_similar_content(query="project discussions", tenant_id="default", limit=10)

# Direct Cypher query
kg.query("MATCH (p:Person)-[:TAKES]->(m:Medication) RETURN m.name")
```

**Entity types:** medication, person, condition, organization, date

**Relationship types:** PRESCRIBED, TREATS, STOPPED, WORKS_AT

**Data produced:**
- Neo4j database at `bolt://neo4j.leadingai.info:7687`
- Episode nodes (content units)
- Entity nodes with properties
- Relationship edges
- Context Cards for all entities

**UI components needed:**
- [ ] Graph visualization (force-directed layout)
- [ ] Entity type filters (checkboxes)
- [ ] Relationship type filters
- [ ] Node click → show details
- [ ] Path finder ("show connection between X and Y")
- [ ] Expand/collapse node neighbors

**Documentation:** [knowledge-stores/GRAPH_STORE.md](./knowledge-stores/GRAPH_STORE.md)

---

## 2.4 PARA Organization

**What it does:** Organizes all knowledge using the PARA methodology (Projects, Areas, Resources, Archives).

**Folder Structure:**
```
/root/flourisha/
├── 01f_Flourisha_Projects/    # Time-bound efforts with outcomes
├── 02f_Flourisha_Areas/       # Ongoing responsibilities
│   ├── Content_Intelligence/
│   ├── Finance/
│   ├── Marketing/             # NEW - GTM strategy lives here
│   └── Yourself/              # Personal context, identity
├── 03f_Flourisha_Resources/   # Reference materials
│   ├── Photos/
│   ├── Chat Sessions/
│   ├── Meeting Transcripts/
│   └── Zettelkasten style notes
└── 04f_Flourisha_Archives/    # Completed/inactive items
```

**UI components needed:**
- [ ] PARA folder browser (tree view)
- [ ] Quick navigation sidebar
- [ ] File preview panel
- [ ] Search within PARA
- [ ] Move items between categories
- [ ] Archive completed projects

---

## 2.5 Memory System

**What it does:** Persistent memory across conversations via Mem0/oMem integration.

**Status:** Planned / Partially implemented

**Memory Types:**
- Session memory (conversation context)
- Long-term memory (facts about user)
- Episodic memory (specific events)
- Semantic memory (learned concepts)

**UI components needed:**
- [ ] Memory browser
- [ ] Memory edit/delete controls
- [ ] Memory source attribution
- [ ] Memory timeline view

---

# 3. STRATEGIC COMMAND [think]

> **Purpose:** The AI Brain that understands who you are and helps you strategize.
>
> **Components:** Context Card (your identity profile), Strategy Agents, Morning Reports, OKR tracking
>
> **Goal:** Move from reactive assistance to proactive strategic partnership

---

## 3.1 Context Card System

**What it does:** A living document that captures who you are - built through conversation, not questionnaires. Powers personalized responses across all of Flourisha.

**Status:** NEW - Core product for $37 tier

**Context Card Contents:**

| Section | Description | Data Sources |
|---------|-------------|--------------|
| **Identity & Values** | Core values, what matters most, self-description | Conversations, explicit statements |
| **Key People** | Important relationships (family, colleagues, friends) | Mentions, relationship context |
| **Thinking Patterns** | Decision-making style, communication preferences | Conversation analysis |
| **Current Focus** | Active projects, goals, priorities | PARA Projects, OKRs |
| **Interests & Knowledge** | Topics engaged with, areas of expertise | Content consumption patterns |
| **Patterns & Preferences** | Productivity patterns, information preferences | Energy tracking, interaction history |

**30 Universal Questions Framework:**

Questions gathered progressively through conversation to map to personality frameworks:

**Phase 1 (First Session - 5-7 questions):**
- "What would you do if money wasn't a concern?"
- "When do you feel most alive/energized?"
- "What do people always come to you for help with?"
- "What pisses you off about how things are done?"
- "If you had to teach something for a year, what would it be?"

**Phase 2 (Over time - 10-15 questions):**
- Decision-making style questions
- Energy/productivity patterns
- Communication preferences
- Risk tolerance
- Learning style

**Framework Mapping (invisible to user):**

| Question Theme | Maps To |
|----------------|---------|
| Energy source (alone/people) | Myers-Briggs E/I, Human Design type |
| Decision style (logic/values) | Myers-Briggs T/F |
| Information processing | Myers-Briggs S/N |
| Structure preference | Myers-Briggs J/P |
| Core motivations | Enneagram type |
| Gift/genius zone | Gene Keys |
| *(Optional)* Birth data | Human Design, Astrology |

**Backend interface:**
```python
# Future API
from services.context_card_service import ContextCardService

service = ContextCardService(user_id)
card = service.get_context_card()
service.update_from_conversation(conversation_id)
service.export_pdf()
```

**UI components needed:**
- [ ] Context Card dashboard view
- [ ] Section-by-section display
- [ ] Edit/correct information controls
- [ ] Export to PDF button
- [ ] Data sources transparency (which conversations)
- [ ] Privacy controls (delete specific items)
- [ ] "Personality twins" feature (famous people with similar profiles)
- [ ] Framework insights (optional deep dive)

**Documentation:** To be created

### Personality Profiles (Contact Extension)

**What it does:** Extends the Context Card concept to your key contacts - capturing communication styles, relationship context, and interaction history for personalized responses (especially email).

**Status:** Phase 3 feature - builds on Context Card foundation

**Personality Profile Contents:**

| Section | Description | Data Sources |
|---------|-------------|--------------|
| **Identity** | Name, role, relationship to user | Explicit input, email signatures |
| **Communication Style** | Formal/casual, brevity preference, response timing | Email analysis, conversation patterns |
| **Topics of Interest** | What they care about, expertise areas | Conversation history |
| **Relationship Context** | How you met, shared history, dynamics | Explicit input, interactions |
| **Interaction Patterns** | Best times to reach, preferred channels | Historical data |

**Storage:** Neo4j knowledge graph (entity nodes with profile properties)

**Use Cases:**
- Email agent drafts responses matching contact's communication style
- Morning report surfaces relevant contacts for follow-up
- Knowledge retrieval enriched with relationship context

**Backend interface:**
```python
# Future API
from services.personality_profile_service import PersonalityProfileService

service = PersonalityProfileService()
profile = service.get_profile(contact_id)
service.update_from_email(email_id)
service.suggest_communication_approach(contact_id, topic)
```

**UI components needed:**
- [ ] Contact profiles list view
- [ ] Individual profile detail view
- [ ] Communication style indicators
- [ ] Relationship timeline
- [ ] Edit/correct information controls
- [ ] Privacy controls

**Integration with Context Card:**
- Your Context Card + Contact's Personality Profile = optimized communication
- Email agent uses both for tone/style matching
- Knowledge queries can filter by relationship context

**Documentation:** [AGENT_FACTORY.md](./services/AGENT_FACTORY.md) (context assembly section)

---

## 3.2 Morning Report

**What it does:** Automated daily intelligence briefing at 7:00 AM Pacific via HTML email. Synthesizes OKR progress, energy forecasts, task priorities, and knowledge insights.

**Backend interface:**
```bash
# Manual trigger
/root/flourisha/00_AI_Brain/scripts/morning_report.sh

# Test mode
python -m services.morning_report_service --test

# Dry run (no email sent)
python -m services.morning_report_service --dry-run
```

**Cron schedule:** `0 7 * * *` (7 AM daily)

**Report sections:**
1. THE ONE THING (highest priority task)
2. Yesterday Recap
3. Today's Plan (time-blocked)
4. OKR Progress (with progress bars)
5. PARA Updates
6. Energy Forecast
7. Knowledge Insights

**THE ONE THING algorithm:**
- 40% OKR Impact
- 30% Urgency
- 20% Energy Match
- 10% Dependencies Cleared

**Data produced:**
- HTML email to gwasmuth@gmail.com
- Queries: energy_tracking, okr_tracking, processed_content, projects

**UI components needed:**
- [ ] Morning report preview (web version)
- [ ] Report history viewer
- [ ] Section customization settings
- [ ] Send now / schedule controls
- [ ] THE ONE THING highlight card

**Configuration:** `/root/flourisha/00_AI_Brain/config/morning_report.json`

**Documentation:** [services/MORNING_REPORT.md](./services/MORNING_REPORT.md)

---

## 3.3 OKR System

**What it does:** Quarterly goal management with Objectives and Key Results. Weekly measurements, progress calculation, status tracking.

**Backend interface:**
```python
from services.okr_service import OKRService

okr = OKRService()

# Create OKR
okr.create_okr(quarter="Q1-2026", objective="title", key_results=[...])

# Update progress
okr.update_kr_progress(kr_id, progress_value)

# Record measurement
okr.record_measurement(kr_id, value, notes)

# Get quarterly view
okrs = okr.get_quarter_okrs("Q1-2026")

# Forecast completion
forecast = okr.forecast_completion(kr_id)
```

**Measurement schedule:** Every Monday at 8:00 AM Pacific

**Status thresholds (at week 8 of 12):**
- ≥70% = ON TRACK (green)
- 50-69% = NEEDS ATTENTION (yellow)
- <50% = AT RISK (red)
- Blocked = BLOCKED (gray)

**Data produced:**
- Database: `okr_tracking` (definitions), `okr_measurements` (history)
- Progress percentages per KR
- Weekly velocity calculations
- Completion forecasts

**UI components needed:**
- [ ] Quarter selector dropdown
- [ ] Objective cards with progress rings
- [ ] Key Results list with progress bars
- [ ] Status badges (ON TRACK, etc.)
- [ ] Measurement input form
- [ ] Historical chart (progress over time)
- [ ] Velocity indicator
- [ ] Forecast date display

**Documentation:** [services/OKR_SYSTEM.md](./services/OKR_SYSTEM.md)

---

## 3.4 Energy Tracking

**What it does:** Real-time energy and focus quality tracking via Chrome extension (90-minute intervals) with SMS fallback. Powers task scheduling optimization.

**Backend interface:**
```python
# Chrome extension → POST to API
POST /webhooks/energy
{
    "energy_level": 8,
    "focus_quality": "deep",
    "current_task": "writing documentation"
}

# SMS format
"8 D" → energy=8, focus=deep
"6 S" → energy=6, focus=shallow
"4 X" → energy=4, focus=distracted

# Forecast
from services.energy_forecast_service import EnergyForecastService
forecast = EnergyForecastService().forecast_daily_energy(date)
```

**Active hours:** Monday-Friday 8 AM - 6 PM Pacific

**Focus quality options:**
- D = Deep (focused work)
- S = Shallow (administrative)
- X = Distracted

**Forecast algorithm:**
- 50% historical pattern
- 30% recent trend
- 20% schedule impact

**Data produced:**
- Database: `energy_tracking` table
- Fields: timestamp, energy_level (1-10), focus_quality, current_task, source

**UI components needed:**
- [ ] Energy input slider (1-10)
- [ ] Focus quality buttons (Deep/Shallow/Distracted)
- [ ] Current task input (optional)
- [ ] Energy timeline chart (last 7 days)
- [ ] Focus quality distribution pie chart
- [ ] Forecast display for today
- [ ] Best hours indicator

**Documentation:** [services/ENERGY_TRACKING.md](./services/ENERGY_TRACKING.md)

---

## 3.5 Daily Roadmap

**What it does:** AI-powered morning planning that synthesizes session history and projects into a focused daily roadmap.

**Backend interface:**
- Skill: `daily-roadmap`
- Trigger: "daily roadmap", "start my day", "morning planning", "what should I focus on today"

**How it works:**
1. Synthesizes recent session history
2. Reviews active projects and deadlines
3. Considers energy patterns and calendar
4. Produces prioritized daily focus areas

**Output format:**
- Top 3 priority items for the day
- Context from recent work
- Recommended focus blocks
- Warnings about upcoming deadlines

**UI components needed:**
- [ ] Daily roadmap display card
- [ ] Priority list with time estimates
- [ ] Calendar integration view
- [ ] "Start my day" quick action button
- [ ] Session history summary

**Documentation:** Skill definition at `~/.claude/skills/daily-roadmap/`

---

# 4. AGENTIC OPERATIONS [execute]

> **Purpose:** Agents and skills that execute work on your behalf.
>
> **Components:** Skills System, Specialized Agents, Long-Running Agent Harness, Fabric Prompts
>
> **Goal:** Delegate and automate while maintaining quality and oversight

---

## 4.1 Skills System

**What it does:** Modular capability framework with self-contained packages of specialized knowledge. Skills activate based on user intent matching.

**Backend interface:**
- Location: `${PAI_DIR}/skills/[skill-name]/`
- Required file: `SKILL.md` (quick reference)
- Optional: `CLAUDE.md` (comprehensive guide)

**Progressive disclosure:**
1. User request → Intent match
2. Load SKILL.md (quick reference)
3. If needed → Load CLAUDE.md (full methodology)
4. Execute workflow

**Available skills:**
- research, daily-roadmap, clickup-tasks
- flourisha-sync, fabric, content-intelligence
- youtube-learning-processor, and more...

**UI components needed:**
- [ ] Skills browser (grid of skill cards)
- [ ] Skill detail view with documentation
- [ ] Skill trigger buttons
- [ ] Skill search
- [ ] Recently used skills

**Documentation:** [pai-system/skills-system.md](./pai-system/skills-system.md)

---

## 4.2 Specialized Agents

**What it does:** Provides specialized AI agents for different domains with specific capabilities and tools.

| Agent | Triggers | Specialization |
|-------|----------|----------------|
| General-Purpose | Default | Complex problem-solving |
| Researcher | "research", "find", "investigate" | Web research, synthesis |
| Engineer | "code", "debug", "implement" | Code implementation |
| Designer | "design", "ui", "ux" | UI/UX, visual testing |
| Pentester | "security", "vulnerability" | Security testing |
| Architect | "architecture", "design system" | Technical specifications |
| Writer | "write", "document", "blog" | Content creation |

**Multi-agent workflows:**
- **Sequential:** Architect → Engineer → Designer → Pentester → Writer
- **Parallel:** Multiple agents for independent tasks

**Long-Running Agent Harness:**
- ClickUp integration for task tracking
- Progress checkpoints
- Human-in-the-loop approvals
- Automatic documentation

**UI components needed:**
- [ ] Agent selector (manual override)
- [ ] Active agent indicator
- [ ] Agent capabilities list
- [ ] Multi-agent workflow builder
- [ ] Agent execution history
- [ ] Long-running task monitor

**Documentation:** [pai-system/agent-system.md](./pai-system/agent-system.md)

---

## 4.3 A2A Protocol (Agent-to-Agent)

**What it does:** Universal agent interoperability standard for communication between AI agents across platforms.

**Registry structure:**
- `agents.json` - All agents with tags and categories
- `skills.json` - Skills with slash command mappings
- `capabilities.json` - System-wide capabilities

**Agent Card format:**
```json
{
    "id": "researcher",
    "name": "Research Agent",
    "version": "1.0.0",
    "capabilities": ["web_search", "synthesis"],
    "skills": ["deep-research", "quick-lookup"]
}
```

**UI components needed:**
- [ ] Agent registry browser
- [ ] Agent card viewer
- [ ] Capability discovery
- [ ] Agent communication logs

**Documentation:** [a2a/overview.md](./a2a/overview.md)

---

## 4.4 Hook System

**What it does:** Event-driven automation at specific points in the AI interaction lifecycle.

**Hook types:**
1. `user-prompt-submit-hook` - Before prompts processed
2. `tool-use-hook` - Before tool execution
3. `post-execution-hook` - After commands complete
4. `response-hook` - Before AI response displayed

**Execution flow:**
```
User Input → user-prompt-submit-hook → AI Processing →
tool-use-hook → Tool Execution → post-execution-hook →
response-hook → User Output
```

**UI components needed:**
- [ ] Hook configuration editor
- [ ] Hook enable/disable toggles
- [ ] Hook execution logs
- [ ] Debug mode toggle

**Documentation:** [pai-system/hook-system.md](./pai-system/hook-system.md)

---

## 4.5 Command System

**What it does:** Custom commands and automation scripts that integrate with PAI infrastructure.

**Command types:**
1. **Instructional** - Markdown files with AI-executable instructions
2. **Executable** - TypeScript/Shell scripts with documentation

**Location:** `${PAI_DIR}/commands/`

**Core commands:**
- `capture-learning` - Problem-solving narrative capture
- `load-dynamic-requirements` - Context loading based on intent
- `web-research` - Perplexity AI integration

**UI components needed:**
- [ ] Command browser
- [ ] Command documentation viewer
- [ ] Quick execute buttons
- [ ] Command creation wizard

**Documentation:** [pai-system/command-system.md](./pai-system/command-system.md)

---

## 4.6 Fabric Prompts

**What it does:** Access to 242+ specialized prompts from Daniel Miessler's Fabric project for content analysis, summarization, extraction, and transformation.

**Skill:** `fabric`

**Common patterns:**
- `extract_wisdom` - Key insights from content
- `summarize` - Concise summaries
- `analyze_claims` - Fact-checking
- `create_keynote` - Presentation generation
- `improve_writing` - Writing enhancement

**UI components needed:**
- [ ] Fabric pattern browser
- [ ] Pattern search
- [ ] Input/output preview
- [ ] Favorite patterns

---

# 5. SYSTEM EVOLUTION [grow]

> **Purpose:** Continuous improvement through feedback loops and infrastructure.
>
> **Components:** Feedback systems, Tech Stack, Security, Infrastructure (Contabo, Sandboxes)
>
> **Feedback Loops:** Updated Documentation, New Skill Patterns, Learned Behaviors, Enhanced Context

---

## 5.1 Extraction Feedback System

**What it does:** Continuous improvement system for document extraction through human review queue, few-shot examples, and automated validation against known entities.

**Backend interface:**
```python
from services.extraction_feedback_service import get_feedback_service

service = get_feedback_service()

# Get documents needing review
queue = service.get_review_queue(limit=20, tenant_id="default")

# Submit corrections
from services.extraction_feedback_service import FeedbackCorrection
corrections = [
    FeedbackCorrection(
        field_name="companies",
        extracted_value={"name": "Wrong Co"},
        corrected_value={"name": "Correct Co"},
        correction_type="incorrect",
        notes="Company name was misspelled"
    )
]
service.submit_correction(document_id, corrections, reviewed_by="user@email.com")

# Get few-shot examples for a category
examples = service.get_few_shot_examples(category="insurance", limit=3)
```

**Database tables:**

| Table | Purpose |
|-------|---------|
| `mrl_extraction_feedback` | Human corrections with context |
| `mrl_extraction_examples` | Curated few-shot examples for prompts |
| `mrl_validation_rules` | Automated validation rule definitions |
| `mrl_validation_results` | Validation outcomes per document |
| `mrl_review_queue` (view) | Documents needing human review |

**UI components needed:**

**Review Queue:**
- [ ] Review queue dashboard with priority sorting
- [ ] Document preview panel (extracted data side-by-side with PDF)
- [ ] Validation failure badges per document
- [ ] Filter by: severity, category, date, validation rule failed
- [ ] Bulk approve/reject controls

**Correction Interface:**
- [ ] Side-by-side view: extracted vs corrected values
- [ ] Field-level correction forms
- [ ] Correction type selector (missing/incorrect/extra/wrong_field)
- [ ] "Promote to Example" button (creates few-shot example)

**Few-Shot Examples Manager:**
- [ ] Examples browser by category
- [ ] Example editor
- [ ] Priority slider
- [ ] Active/inactive toggle

**Documentation:** [database/migrations/003_extraction_feedback.sql](../database/migrations/003_extraction_feedback.sql)

---

## 5.2 Extraction Backends

**What it does:** Strategy pattern with three backends for document extraction with automatic fallback.

| Backend | Speed | Cost | Accuracy | Use Case |
|---------|-------|------|----------|----------|
| Claude | Medium | API tokens | Excellent | Medical, complex layouts |
| Docling | Fast | Free | Good | Batch processing, simple docs |
| Legacy | Fast | Free | Basic | Plain text, simple PDFs |

**UI components needed:**
- [ ] Backend status indicators
- [ ] Backend selector for manual override
- [ ] Fallback chain visualization
- [ ] Health check buttons

**Documentation:** [services/EXTRACTION_BACKENDS.md](./services/EXTRACTION_BACKENDS.md)

---

## 5.3 Voice System

**What it does:** Text-to-speech notifications using ElevenLabs. Distinct voices for Kai and each specialized agent.

**Backend interface:**
```bash
# Server on port 8888
POST /notify
{
    "message": "Task completed successfully",
    "voice_id": "optional_voice_id",
    "title": "optional_title"
}

POST /pai  # Uses default voice
GET /health
```

**Completion format required:** `🎯 COMPLETED: [description]`

**Custom voice:** `🗣️ CUSTOM COMPLETED: [short version < 8 words]`

**Voice mappings:**
| Agent | Voice ID |
|-------|----------|
| Kai | s3TPKV1kjDlVtZbl4Ksh |
| Perplexity-Researcher | AXdMgz6evoL7OPd7eU12 |
| Engineer | fATgBRI8wg5KkDFg8vBd |
| Designer | ZF6FPAbjXT4488VcRRnw |
| Pentester | xvHLFjaUEpx4BOf7EiDd |

**UI components needed:**
- [ ] Voice enable/disable toggle
- [ ] Voice selector dropdown
- [ ] Test voice button
- [ ] Volume control

**Documentation:** [pai-system/voice-system.md](./pai-system/voice-system.md)

---

## 5.4 ClickUp Integration

**What it does:** Task management with Idea Scratchpad and project lists.

**Key lists:**
- Idea Scratchpad (ID: 901112609506) - Quick idea capture
- Project-specific lists

**Skill:** `clickup-tasks`

**UI components needed:**
- [ ] Quick idea capture input
- [ ] Task list view
- [ ] Status updates
- [ ] Priority assignment
- [ ] Task detail modal

---

## 5.5 System Monitoring (Netdata)

**What it does:** Real-time system monitoring with 1-second granularity. CPU, RAM, disk, network metrics.

**Access:** http://100.66.28.67:19999 (Tailscale VPN)

**Alerts:** Email to gwasmuth@gmail.com

**UI components needed:**
- [ ] Embed Netdata dashboard (iframe)
- [ ] Key metrics summary cards
- [ ] Alert history list

---

## 5.6 Uptime Monitoring (Uptime Kuma)

**What it does:** Service health monitoring with public status pages.

**Access:** http://100.66.28.67:3001

**Monitor types:** HTTP, TCP, Ping, DNS

**UI components needed:**
- [ ] Service status grid
- [ ] Uptime percentages
- [ ] Incident timeline

---

## 5.7 Playwright MCP (Browser Automation)

**What it does:** Automated browser testing and visual validation within Claude Code sessions.

**Backend interface:**
```
Tools: browser_start, browser_navigate, browser_click,
       browser_type, browser_screenshot, browser_wait,
       browser_evaluate
```

**Data produced:** Screenshots (PNG), DOM content, test results

**UI components needed:**
- [ ] Screenshot viewer
- [ ] Test results panel
- [ ] Browser action log

**Documentation:** [mcp-servers/PLAYWRIGHT_MCP_SETUP.md](./mcp-servers/PLAYWRIGHT_MCP_SETUP.md)

---

## 5.8 Database Layer

**Tables:**

| Table | Purpose |
|-------|---------|
| `processed_content` | Ingested content with embeddings |
| `projects` | Project definitions |
| `input_sources` | Content sources |
| `processing_queue` | Async job queue |
| `youtube_subscriptions` | Channel subscriptions |
| `energy_tracking` | Energy/focus records |
| `okr_tracking` | OKR definitions |
| `okr_measurements` | OKR measurement history |
| `agent_feedback` | Agent execution quality ratings |

**Security:** Row-Level Security (RLS) for multi-tenant isolation

**Visibility controls:** 'private', 'tenant', 'group'

**UI components needed:**
- [ ] Data explorer (admin only)
- [ ] RLS testing interface

**Documentation:** [database/DATABASE_SCHEMA.md](./database/DATABASE_SCHEMA.md)

---

# 6. Frontend Architecture

---

## 6.1 Recommended Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Framework | Next.js 14+ | React + API routes + SSR |
| Styling | Chakra UI | Accessible component library with built-in theming |
| Animation | GSAP | Production-grade motion and transitions |
| State | React Query (TanStack) | Server state management |
| Forms | React Hook Form + Zod | Type-safe validation |
| Markdown | react-markdown + remark | Render processed content |
| Charts | Recharts | OKR progress, energy trends |
| Graph | react-force-graph | Knowledge graph visualization |
| Database | Supabase client | Real-time subscriptions |
| Auth | Supabase Auth | OAuth, session management |
| Payments | Stripe | $37 one-time + subscriptions |

---

## 6.2 API Layer Needs

Most backend services are Python CLI tools. Frontend needs:

1. **REST API wrapper** around CLI commands
2. **WebSocket** for long-running processes (video processing)
3. **Progress streaming** for user feedback
4. **File reading** for markdown content

**Suggested API Routes:**

```
/api/youtube/playlists          GET    - List playlists
/api/youtube/process            POST   - Process videos
/api/youtube/channels           GET    - List channels
/api/documents/upload           POST   - Upload document
/api/documents/process          POST   - Process document
/api/search                     POST   - Unified search
/api/okr                        GET    - Get OKRs
/api/okr/measure                POST   - Record measurement
/api/energy                     POST   - Log energy
/api/energy/forecast            GET    - Get forecast
/api/sync/trigger               POST   - Trigger sync
/api/sync/status                GET    - Sync status
/api/context-card               GET    - Get user's Context Card
/api/context-card/export        POST   - Export to PDF
/api/blueprints/business        POST   - Generate Business Blueprint
```

---

## 6.3 Priority Implementation Order

### Phase 1: Foundation + Entry Point (Weeks 1-2)
- [ ] Next.js setup with Chakra UI + GSAP
- [ ] Landing page with pricing
- [ ] Basic chat interface (thinking partner)
- [ ] Free tier with session memory
- [ ] Stripe integration ($37 purchase)

### Phase 2: Context Card / Blueprint (Weeks 3-4)
- [ ] 30 Questions progressive gathering
- [ ] Context Card generation
- [ ] Business Blueprint output
- [ ] PDF export
- [ ] Framework mapping (invisible)

### Phase 3: Knowledge Exploration (Weeks 5-6)
- [ ] Semantic search
- [ ] Graph explorer
- [ ] PARA browser
- [ ] Results ranking

### Phase 4: Productivity Tools (Weeks 7-8)
- [ ] OKR dashboard
- [ ] Energy tracking
- [ ] Morning report viewer
- [ ] Daily planning

### Phase 5: System Management (Weeks 9-10)
- [ ] Skills browser
- [ ] Agent status
- [ ] Sync controls
- [ ] Settings

---

## Feature Request Template

When adding new backend features, add to this registry:

```markdown
### [Feature Name]

**What it does:** [User-facing description]

**Backend interface:**
```bash
[CLI commands or API endpoints]
```

**Data produced:** [Where outputs live]

**UI components needed:**
- [ ] [Component 1]
- [ ] [Component 2]

**Documentation:** [Link to detailed docs]
```

---

*This document is the source of truth for frontend development. Update whenever backend capabilities change.*

*Organized by the Five Pillars: INGEST → KNOW → THINK → EXECUTE → GROW*

*Last updated: 2025-12-15*
