# [Flourisha AI] System Specification
## The Canonical Reference for Autonomous Development

*Last Updated: 2025-12-18 16:20 PT*

---

## Table of Contents

- [Flourisha AI System Specification](#flourisha-ai-system-specification)
  - [Changelog (Last 10 Updates)](#changelog-last-10-updates)
  - [Vision & Mission](#vision--mission)
  - [What is Flourisha?](#what-is-flourisha)
  - [Platform Overview](#platform-overview)
  - [Multi-Workspace Architecture](#multi-workspace-architecture)
  - [Integrations Architecture](#integrations-architecture)
  - [Quick Navigation](#quick-navigation)
  - [The Five Pillars Architecture](#the-five-pillars-architecture)
- [1. INGEST (Content Ingestion)](#1-ingest-content-ingestion)
  - [Features](#features)
  - [Architecture](#architecture)
  - [PDF Ingestion & Processing](#pdf-ingestion--processing)
  - [Gmail Integration](#gmail-integration)
  - [Content Processing Queue](#content-processing-queue)
  - [Key Files](#key-files)
- [2. KNOW (Knowledge Hub)](#2-know-knowledge-hub)
  - [Features](#features-1)
  - [Three-Store Architecture](#three-store-architecture)
  - [Key Files](#key-files-1)
- [3. THINK (Strategic Command)](#3-think-strategic-command)
  - [Features](#features-2)
  - [Morning Report System](#morning-report-system)
  - [Energy Tracking System](#energy-tracking-system)
  - [Key Files](#key-files-2)
- [4. EXECUTE (Agentic Operations)](#4-execute-agentic-operations)
  - [Features](#features-3)
  - [Skills Architecture](#skills-architecture)
  - [Agent Types](#agent-types)
  - [Agent Factory Pattern](#agent-factory-pattern)
  - [Automation Schedule (Cron Jobs)](#automation-schedule-cron-jobs)
  - [Key Files](#key-files-3)
- [5. GROW (System Evolution)](#5-grow-system-evolution)
  - [Features](#features-4)
  - [Feedback Loop Types](#feedback-loop-types)
  - [Success Metrics](#success-metrics)
  - [Key Files](#key-files-4)
  - [Technology Stack](#technology-stack)
  - [Authentication Architecture](#authentication-architecture)
  - [Infrastructure](#infrastructure)
  - [MyRemoteLender Migration (Airtable + Make.com → Supabase)](#myremoteLender-migration-airtable--makecom--supabase)
  - [PARA Folder Structure](#para-folder-structure)
  - [Autonomous Development](#autonomous-development)
  - [Autonomous Update Protocol](#autonomous-update-protocol)
  - [Document Hierarchy](#document-hierarchy)
  - [Active Enhancement Plans](#active-enhancement-plans)
  - [Contact & Identity](#contact--identity)

---

## Changelog (Last 10 Updates)

| Date | Time | Change |
|------|------|--------|
| 2025-12-18 | 16:20 PT | Organized plans/ under documentation/, added Active Enhancement Plans section |
| 2025-12-18 | 13:07 PT | Synced with mindmap - added 14 missing items across all 5 pillars |
| 2025-12-18 | 12:45 PT | Added Chrome Extension to Platform Overview with features table |
| 2025-12-18 | 12:30 PT | Added Firebase Dynamic Links / Deep Linking (planned) |
| 2025-12-18 | 12:15 PT | Fixed auth: Supabase Auth → Firebase Auth, added Authentication Architecture section |
| 2025-12-18 | 11:45 PT | Added PDF Ingestion section (Claude primary, Docling backup) |
| 2025-12-18 | 11:30 PT | Added Vision & Mission section |
| 2025-12-18 | 11:15 PT | Added Platform Overview with Mobile stack |
| 2025-12-18 | 11:00 PT | Added Integration Architecture (MCP vs Direct API vs Skill) |
| 2025-12-18 | 10:45 PT | Updated Frontend stack: Chakra UI, GSAP |

---

## Vision & Mission

### The Problem We're Solving

We're hyperconnected to 10,000 people—and not one calls when we're sick.

The modern world has given us unprecedented access to information, networks, and productivity tools. Yet we're starving for something more fundamental: **recognition**. The feeling that someone truly understands us. Not our social media highlight reel. Not our professional resume. *Us.*

Most AI is designed to extract, automate, or replace. Flourisha is different.

### Our Vision

**A thinking friend that helps you become more of who you want to be.**

Not replacing human connection. Not tricking people into engagement. Not optimizing for metrics that don't matter.

Flourisha creates presence—an AI that knows you deeply, reflects you back to yourself, and helps you see your own potential more clearly. When someone has their first session with Flourisha, we want them to feel genuinely *understood*. Not surface-level personalization, but real comprehension of who they are.

### Why This Matters

The skeptic says: "AI can't really understand me."

We believe the opposite. AI can hold context that humans forget. It can notice patterns across years of your thinking. It can remember what matters to you when the chaos of life makes you forget yourself. A journalist's AI could help her clarify her own insights, challenge her assumptions, and push her toward the stories only she can tell—not replacing her editor or sources, but making her sharper.

This isn't about AI capability. It's about AI *purpose*.

### Our Mission

**Be More.**

Not "Do More." Not "Optimize." Not "Automate."

*Be More.*

Flourisha exists to help people become more fully themselves. We're building AI that:
- **Recognizes** you as a whole person, not a collection of data points
- **Amplifies** your strengths instead of replacing your effort
- **Connects** your scattered thoughts into coherent insight
- **Remembers** what matters when you're too busy to remember yourself
- **Grows** with you, learning your patterns and aspirations over time

When Flourisha works, you feel seen. You feel understood. And from that foundation of recognition, you have the clarity and confidence to be more of who you want to be.

---

## What is Flourisha?

Flourisha is a **Personal AI Infrastructure (PAI)** system built on Claude Code that manages knowledge, productivity, and AI-assisted workflows. It serves as Greg Wasmuth's AI chief of staff but will grow into supporting millions of Organizations and people.

**Key Capabilities:**
- Ingest content from anywhere (YouTube, documents, email, web)
- Store knowledge in three complementary systems (Vector, Graph, Whole)
- Provide strategic assistance (morning reports, OKRs, Habit tracking)
- Execute work via specialized agents (research, engineering, design)
- Continuously improve through feedback loops

---

## Platform Overview

Flourisha is a **cross-platform application** available on:

| Platform | Technology | Status |
|----------|------------|--------|
| **Web App** | Next.js 14+ | Primary development |
| **iOS App** | React Native (Expo) | Planned |
| **Android App** | React Native (Expo) | Planned |
| **Chrome Extension** | Chrome Extension API | Working (Energy), Planned (Capture) |

### Why Cross-Platform?

Your thinking friend should be with you wherever you are—at your desk, on your commute, in the moment when an idea strikes. The mobile apps aren't just responsive web views; they're native apps with **device-native capabilities**.

### Mobile-Specific Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Photo Capture** | Take photos directly into Flourisha | Capture whiteboards, documents, ideas, receipts |
| **Voice Memos** | Record voice notes with transcription | Capture thoughts on the go |
| **Voice Conversations** | Full voice interaction with AI | Hands-free AI assistance |
| **Speaker Diarization** | Identify who said what in recordings | Meeting notes, interviews, conversations |

### Chrome Extension Features

| Feature | Status | Description | Use Case |
|---------|--------|-------------|----------|
| **Energy Tracking** | ✅ Working | Popup for energy/focus logging | 90-minute interval check-ins during work |
| **Quick Capture** | 🔄 Planned | Capture web content, highlights, notes | Save articles, quotes, ideas while browsing |
| **Page Context** | 🔄 Planned | Send current page to Flourisha | "Summarize this", "Add to knowledge base" |

### Voice Conversation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE CONVERSATION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📱 Mobile App                                                   │
│  └─ Records audio stream                                        │
│                                                                  │
│        ↓                                                         │
│                                                                  │
│  🎙️ Speech-to-Text Service (Deepgram/AssemblyAI)                │
│  ├─ Real-time transcription                                     │
│  ├─ Speaker diarization (who said what)                         │
│  └─ Timestamped segments                                        │
│                                                                  │
│        ↓                                                         │
│                                                                  │
│  🧠 Flourisha AI Processing                                      │
│  ├─ Context from your knowledge stores                          │
│  ├─ Understanding of all participants                           │
│  └─ Intelligent responses                                       │
│                                                                  │
│        ↓                                                         │
│                                                                  │
│  🔊 Text-to-Speech (ElevenLabs)                                  │
│  └─ Natural voice response                                      │
│                                                                  │
│        ↓                                                         │
│                                                                  │
│  💾 Storage                                                      │
│  ├─ Full transcript with speaker labels                         │
│  ├─ Key insights extracted                                      │
│  └─ Ingested to knowledge stores                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Platform Parity Strategy

| Feature | Web | iOS | Android | Chrome Ext |
|---------|-----|-----|---------|------------|
| Dashboard & Analytics | ✓ | ✓ | ✓ | — |
| Knowledge Search | ✓ | ✓ | ✓ | — |
| Content Ingestion | ✓ | ✓ | ✓ | 🔄 Planned |
| Voice Chat | ✓ | ✓ | ✓ | — |
| **Photo Capture** | Limited | ✓ Native | ✓ Native | — |
| **Voice Memos** | ✓ | ✓ Native | ✓ Native | — |
| **Speaker Diarization** | ✓ | ✓ | ✓ | — |
| Push Notifications | Limited | ✓ Native | ✓ Native | — |
| Offline Mode | PWA | ✓ | ✓ | — |
| Widgets | — | ✓ | ✓ | — |
| **Energy Tracking** | ✓ | ✓ | ✓ | ✓ Primary |
| **Quick Web Capture** | — | — | — | 🔄 Planned |

---

## Multi-Workspace Architecture

> **The Big Idea:** Unlike traditional multi-tenant SaaS where organizations own users, Flourisha uses a **user-centric model** where the USER is the primary entity and WORKSPACES are things they JOIN. This is the pattern used by ClickUp, Slack, Notion, GitHub, and Discord.

### Why This Matters for Personal AI

When you bring your Personal AI (Flourisha) to a company:
- **Your AI stays yours** - Your personal knowledge, context, and learning remain with you
- **Companies get AI-enhanced workers** - Your AI can operate within their workspace with appropriate boundaries
- **Clean separation** - Work products stay with the company, personal intelligence stays with you
- **Portable identity** - When you leave, you take your AI with its accumulated personal knowledge

### Core Concepts

#### 1. User-Centric vs Tenant-Centric

| Traditional Multi-Tenant | Flourisha Multi-Workspace |
|--------------------------|---------------------------|
| Tenant is primary entity | **User** is primary entity |
| Users belong to tenants | Users **JOIN** workspaces |
| `tenant_id` is primary key | `user_id` is primary key |
| One tenant per user | **Multiple workspaces** per user |
| Tenant owns user data | User owns personal data |
| Hard to leave with data | **Built-in data portability** |

#### 2. Workspace Model (Like ClickUp/Slack/Notion)

```
                    ┌─────────────────────────────────────────────────────┐
                    │                     USER (Primary Entity)            │
                    │  email: user@example.com                            │
                    │  personal_workspace: Always exists, always free     │
                    │  context_card: Tiered visibility                    │
                    └─────────────────────┬───────────────────────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────────┐
              │                           │                               │
              ▼                           ▼                               ▼
   ┌──────────────────┐      ┌──────────────────┐           ┌──────────────────┐
   │ Personal Space   │      │ Company A        │           │ Company B        │
   │ (Always Free)    │      │ Workspace        │           │ Workspace        │
   │                  │      │                  │           │                  │
   │ • Private notes  │      │ Role: Member     │           │ Role: Guest      │
   │ • Personal AI    │      │ Billing: Paid    │           │ Billing: Limited │
   │ • Learning       │      │ Access: Full     │           │ Access: Scoped   │
   │ • Context cards  │      │                  │           │                  │
   └──────────────────┘      └──────────────────┘           └──────────────────┘
```

#### 3. Membership Roles

| Role | Access Level | Billing | Use Case |
|------|-------------|---------|----------|
| **Owner** | Full admin | Workspace pays | Created the workspace |
| **Admin** | Manage members, settings | Workspace pays | Trusted team leads |
| **Member** | Full workspace access | Workspace pays per seat | Employees, core team |
| **Guest** | Limited, project-scoped | Free or reduced rate | Contractors, clients |
| **External** | Read-only, specific items | Free | Stakeholders, reviewers |

#### 4. Context Cards (Tiered Visibility)

Each user has a **Context Card** that presents different information based on relationship level:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONTEXT CARD TIERS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PUBLIC TIER (visibility: 'public')                                         │
│  ├─ Name, professional headline                                             │
│  ├─ Public portfolio/work                                                   │
│  ├─ Social links (if enabled)                                               │
│  └─ Generic AI capabilities                                                 │
│                                                                             │
│  FRIENDS TIER (visibility: 'friends')                                       │
│  ├─ Everything in Public, plus:                                             │
│  ├─ Personal interests, hobbies                                             │
│  ├─ Fun side of personality                                                 │
│  ├─ Life context (family, location)                                         │
│  └─ Personal AI preferences                                                 │
│                                                                             │
│  WORK TIER (visibility: 'work')                                             │
│  ├─ Everything in Public, plus:                                             │
│  ├─ Professional skills & experience                                        │
│  ├─ Work style & communication preferences                                  │
│  ├─ Current projects (non-confidential)                                     │
│  └─ AI working patterns                                                     │
│                                                                             │
│  WORKSPACE TIER (visibility: 'workspace:ID')                                │
│  ├─ Work tier, plus:                                                        │
│  ├─ Workspace-specific role & permissions                                   │
│  ├─ Work products created in that workspace                                 │
│  ├─ Workspace-scoped AI context                                             │
│  └─ Org-specific preferences & training                                     │
│                                                                             │
│  PRIVATE TIER (visibility: 'private')                                       │
│  ├─ Full personal context (only you see this)                               │
│  ├─ Private notes, ideas, drafts                                            │
│  ├─ Personal AI learnings                                                   │
│  └─ Cross-workspace synthesis                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Database Schema Evolution

The current schema uses `tenant_id` as primary isolation. We evolve this to a **user-centric model**:

#### Core Tables (User-Centric)

```sql
-- Users table (PRIMARY entity - users own their identity)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Personal workspace (always exists, always free)
    personal_workspace_id UUID REFERENCES workspaces(id),

    -- Context card with tiered visibility
    context_card JSONB DEFAULT '{
        "public": {},
        "friends": {},
        "work": {},
        "private": {}
    }'::jsonb,

    -- Subscription status (for premium personal features)
    subscription_tier VARCHAR(20) DEFAULT 'free',

    -- AI-specific
    ai_personality_config JSONB DEFAULT '{}'::jsonb,
    ai_memory_preferences JSONB DEFAULT '{}'::jsonb
);

-- Workspaces table (things users JOIN)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Billing (workspace pays, not users)
    billing_email VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    seat_count INTEGER DEFAULT 5,

    -- Type: 'personal' (1 user, free forever) or 'team'
    workspace_type VARCHAR(20) DEFAULT 'team',

    -- Settings
    settings JSONB DEFAULT '{}'::jsonb,
    ai_settings JSONB DEFAULT '{}'::jsonb
);

-- User-Workspace memberships (junction table)
CREATE TABLE workspace_memberships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Role within this workspace
    role VARCHAR(20) DEFAULT 'member',  -- owner, admin, member, guest, external

    -- What tier of context card this workspace sees
    context_visibility VARCHAR(20) DEFAULT 'work',  -- public, friends, work, workspace

    -- Workspace-specific profile override
    workspace_profile JSONB DEFAULT '{}'::jsonb,

    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, pending, suspended
    invited_by UUID REFERENCES users(id),
    joined_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, workspace_id)
);
```

#### Resource Ownership Model

```sql
-- Resources can be owned by USER (portable) or WORKSPACE (stays)
CREATE TABLE resources (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_user_id UUID REFERENCES users(id),

    -- Ownership: 'user' (portable) or 'workspace' (stays with org)
    ownership_type VARCHAR(20) NOT NULL,  -- 'user' or 'workspace'
    owner_id UUID NOT NULL,  -- user_id OR workspace_id based on ownership_type

    -- Visibility within workspace
    workspace_id UUID REFERENCES workspaces(id),
    visibility VARCHAR(50) DEFAULT 'private',

    -- Content
    resource_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,

    -- For workspace-owned: explicitly marked as "work product"
    is_work_product BOOLEAN DEFAULT FALSE
);

-- RLS Policy for resource access
CREATE POLICY "resource_access" ON resources
FOR ALL USING (
    -- User owns the resource personally
    (ownership_type = 'user' AND owner_id = current_user_id())
    OR
    -- User is member of workspace that owns resource
    (ownership_type = 'workspace' AND owner_id IN (
        SELECT workspace_id FROM workspace_memberships
        WHERE user_id = current_user_id() AND status = 'active'
    ))
);
```

#### Processed Content (Updated)

```sql
-- Content now has clear ownership semantics
CREATE TABLE processed_content (
    id UUID PRIMARY KEY,

    -- Owner (user or workspace)
    ownership_type VARCHAR(20) NOT NULL DEFAULT 'user',
    owner_id UUID NOT NULL,

    -- Creator (always a user)
    created_by_user_id UUID REFERENCES users(id) NOT NULL,

    -- Workspace context (where it was created/shared)
    workspace_id UUID REFERENCES workspaces(id),

    -- Visibility
    visibility VARCHAR(50) DEFAULT 'private',
    shared_with JSONB DEFAULT '[]'::jsonb,

    -- Content fields...
    source_type VARCHAR(50) NOT NULL,
    title VARCHAR(1000),
    content TEXT,
    embedding vector(1536),

    -- Data portability flag
    is_portable BOOLEAN GENERATED ALWAYS AS (ownership_type = 'user') STORED,
    is_work_product BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Data Ownership Rules

| Data Type | Default Owner | On Leave Workspace | Example |
|-----------|---------------|-------------------|---------|
| Personal notes | User | **Takes with them** | Private journal, ideas |
| Personal AI memory | User | **Takes with them** | Learning, preferences |
| Context card (personal) | User | **Takes with them** | Skills, personality |
| Work products | Workspace | **Stays with org** | Reports, documents |
| Shared content | Depends | Based on flag | Varies |
| Workspace-specific AI training | Workspace | **Stays with org** | Company-specific patterns |
| Cross-workspace synthesis | User | **Takes with them** | Personal learnings |

### Billing Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BILLING MODEL                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PERSONAL WORKSPACE (Free Forever)                                          │
│  ├─ Every user gets one automatically                                       │
│  ├─ Basic AI features, limited storage                                      │
│  ├─ Can upgrade to Personal Pro ($X/month)                                  │
│  └─ Never loses access to personal data                                     │
│                                                                             │
│  TEAM WORKSPACE (Paid Per Seat)                                             │
│  ├─ Free tier: Up to 3 members, basic features                             │
│  ├─ Team tier: $X/member/month, full features                              │
│  ├─ Business tier: $X/member/month, advanced AI + admin                    │
│  └─ Enterprise: Custom pricing, SSO, compliance                            │
│                                                                             │
│  GUEST ACCESS (Reduced/Free)                                                │
│  ├─ Guests don't count against seat limits                                 │
│  ├─ Limited access (specific projects/channels)                            │
│  └─ Upgrade path to member if needed                                       │
│                                                                             │
│  VIRAL MECHANICS                                                            │
│  ├─ Invite others → Workspace grows naturally                              │
│  ├─ Free tier is genuinely useful (not crippled)                           │
│  ├─ Upgrade when team size > 3 or need advanced features                   │
│  └─ Personal AI follows user across workspaces                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Roles, Groups & Permissions

> **The Hierarchy:** USER → WORKSPACE → GROUPS. A user joins a workspace with a role, and within that workspace they can belong to multiple groups. Permissions flow from both role AND group membership.

#### Access Control Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ACCESS CONTROL HIERARCHY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER (Global Identity)                                                     │
│  └─► WORKSPACE MEMBERSHIP (Role: owner/admin/member/guest)                 │
│       └─► GROUP MEMBERSHIPS (Within that workspace)                        │
│            ├─► "engineering"                                                │
│            ├─► "product"                                                    │
│            ├─► "leadership"                                                 │
│            └─► "contractors"                                                │
│                                                                             │
│  PERMISSION CHECK:                                                          │
│  Can user access resource?                                                  │
│  1. Is user a member of this workspace? (required)                         │
│  2. Does user's ROLE allow this action? (role-based)                       │
│  3. Is resource shared with user's GROUPS? (group-based)                   │
│  4. Is resource explicitly shared with this user? (user-based)             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Workspace Roles (Membership Level)

| Role | Permissions | Billing Impact | Typical Use |
|------|-------------|----------------|-------------|
| **Owner** | Full control: billing, delete workspace, transfer ownership | Counts as seat | Founder, CEO |
| **Admin** | Manage members, groups, settings, integrations | Counts as seat | Team leads, IT |
| **Member** | Full workspace access, create/edit content, join groups | Counts as seat | Employees |
| **Guest** | Limited to specific projects/channels, no admin access | Free or reduced | Contractors, clients |
| **External** | Read-only access to explicitly shared items | Free | Stakeholders, auditors |

#### Groups (Workspace-Scoped)

Groups exist **within** a workspace and enable fine-grained content sharing:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GROUPS WITHIN A WORKSPACE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WORKSPACE: "Acme Corp"                                                     │
│  │                                                                          │
│  ├─► Group: "engineering"                                                   │
│  │   ├─ Members: alice@, bob@, charlie@                                     │
│  │   ├─ Can see: Technical docs, code repos, sprint boards                 │
│  │   └─ AI Context: Technical terminology, codebase patterns               │
│  │                                                                          │
│  ├─► Group: "product"                                                       │
│  │   ├─ Members: diana@, eve@                                               │
│  │   ├─ Can see: PRDs, roadmaps, customer research                         │
│  │   └─ AI Context: Product strategy, user personas                        │
│  │                                                                          │
│  ├─► Group: "leadership"                                                    │
│  │   ├─ Members: alice@, diana@, frank@ (CEO)                               │
│  │   ├─ Can see: Financials, strategic plans, HR docs                      │
│  │   └─ AI Context: Executive summaries, board materials                   │
│  │                                                                          │
│  └─► Group: "all-hands"                                                     │
│      ├─ Members: Everyone in workspace                                      │
│      ├─ Can see: Company announcements, policies                           │
│      └─ AI Context: Company culture, public info                           │
│                                                                             │
│  NOTE: alice@ is in BOTH "engineering" AND "leadership"                     │
│  She sees the UNION of what both groups can access                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Permission Scopes

| Scope | Description | Example |
|-------|-------------|---------|
| `workspace:*` | All members of workspace can access | Company announcements |
| `group:engineering` | Only engineering group members | Technical specs |
| `group:leadership,product` | Multiple groups (OR logic) | Strategic roadmap |
| `user:alice@example.com` | Specific user only | 1:1 shared doc |
| `private` | Only the creator | Personal notes |

#### Projects & PARA Integration

Projects live within the PARA framework and can be shared across workspaces:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROJECTS WITHIN PARA FRAMEWORK                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PERSONAL WORKSPACE (Greg's)                                                │
│  └─► PARA Structure                                                         │
│       ├─► 01_Projects/                                                      │
│       │    ├─► client-acme-audit/  (shared with Acme workspace)            │
│       │    ├─► personal-side-project/  (private)                           │
│       │    └─► consulting-toolkit/  (shared with multiple workspaces)      │
│       ├─► 02_Areas/                                                         │
│       ├─► 03_Resources/                                                     │
│       └─► 04_Archives/                                                      │
│                                                                             │
│  COMPANY WORKSPACE (Acme Corp)                                              │
│  └─► Workspace Projects                                                     │
│       ├─► product-launch-q1/  (group:product,engineering)                  │
│       ├─► infrastructure-upgrade/  (group:engineering)                     │
│       └─► company-handbook/  (visibility:workspace - everyone)             │
│                                                                             │
│  SHARING: Personal projects can be "mounted" into workspace contexts       │
│  OWNERSHIP: Clear distinction between user-owned and workspace-owned       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Project Sharing Rules:**
- Personal projects (user-owned) can be shared INTO workspaces
- Workspace projects stay with the workspace when user leaves
- Files inherit project visibility unless explicitly overridden
- PARA structure is preserved per-workspace (each workspace can have its own PARA)

#### Database Schema for Groups

```sql
-- Groups table (workspace-scoped, with hierarchy support)
CREATE TABLE workspace_groups (
    id UUID PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Hierarchy (enables Teams → Departments → Divisions)
    parent_group_id UUID REFERENCES workspace_groups(id) ON DELETE SET NULL,
    hierarchy_level INTEGER DEFAULT 0,  -- 0=top-level, 1=child, 2=grandchild, etc.

    -- Group identity
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,

    -- Group type
    group_type VARCHAR(20) DEFAULT 'custom',  -- 'system' (all-hands, admins) or 'custom'
    is_default BOOLEAN DEFAULT FALSE,  -- Auto-join for new members?

    -- Suggested hierarchy types (flexible, not enforced)
    hierarchy_type VARCHAR(20),  -- 'team', 'department', 'division', 'project', 'custom'

    -- Settings
    settings JSONB DEFAULT '{}'::jsonb,

    -- AI context for this group
    ai_context JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    UNIQUE(workspace_id, slug)
);

-- Index for hierarchy traversal
CREATE INDEX idx_groups_parent ON workspace_groups(parent_group_id);
CREATE INDEX idx_groups_workspace_hierarchy ON workspace_groups(workspace_id, hierarchy_level);

-- Example hierarchy:
-- Division: "Engineering" (parent_group_id: NULL, hierarchy_level: 0)
--   └─► Department: "Backend" (parent_group_id: engineering_id, hierarchy_level: 1)
--         └─► Team: "API Team" (parent_group_id: backend_id, hierarchy_level: 2)

-- Function to get all ancestor groups (for permission inheritance)
CREATE OR REPLACE FUNCTION get_group_ancestors(p_group_id UUID)
RETURNS TABLE(group_id UUID, group_name VARCHAR, level INTEGER) AS $$
WITH RECURSIVE ancestors AS (
    SELECT id, name, hierarchy_level, parent_group_id
    FROM workspace_groups WHERE id = p_group_id
    UNION ALL
    SELECT wg.id, wg.name, wg.hierarchy_level, wg.parent_group_id
    FROM workspace_groups wg
    JOIN ancestors a ON wg.id = a.parent_group_id
)
SELECT id, name, hierarchy_level FROM ancestors;
$$ LANGUAGE sql SECURITY DEFINER;

-- Function to get all descendant groups (for reporting)
CREATE OR REPLACE FUNCTION get_group_descendants(p_group_id UUID)
RETURNS TABLE(group_id UUID, group_name VARCHAR, level INTEGER) AS $$
WITH RECURSIVE descendants AS (
    SELECT id, name, hierarchy_level, parent_group_id
    FROM workspace_groups WHERE id = p_group_id
    UNION ALL
    SELECT wg.id, wg.name, wg.hierarchy_level, wg.parent_group_id
    FROM workspace_groups wg
    JOIN descendants d ON wg.parent_group_id = d.id
)
SELECT id, name, hierarchy_level FROM descendants;
$$ LANGUAGE sql SECURITY DEFINER;

-- User-Group memberships (within a workspace)
CREATE TABLE group_memberships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    group_id UUID REFERENCES workspace_groups(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Role within the group (optional, for group-level hierarchy)
    group_role VARCHAR(20) DEFAULT 'member',  -- 'lead', 'member'

    -- When they joined
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    added_by UUID REFERENCES users(id),

    UNIQUE(user_id, group_id)
);

-- Index for fast group membership lookups
CREATE INDEX idx_group_memberships_user_workspace
ON group_memberships(user_id, workspace_id);

-- Function to get all groups for a user in a workspace
CREATE OR REPLACE FUNCTION get_user_groups(p_user_id UUID, p_workspace_id UUID)
RETURNS TABLE(group_slug VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT wg.slug
    FROM workspace_groups wg
    JOIN group_memberships gm ON gm.group_id = wg.id
    WHERE gm.user_id = p_user_id
      AND gm.workspace_id = p_workspace_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

#### Resource Visibility with Groups

```sql
-- Updated processed_content with group-based visibility
CREATE TABLE processed_content (
    id UUID PRIMARY KEY,

    -- Ownership (user or workspace)
    ownership_type VARCHAR(20) NOT NULL DEFAULT 'user',
    owner_id UUID NOT NULL,
    created_by_user_id UUID REFERENCES users(id) NOT NULL,

    -- Workspace context
    workspace_id UUID REFERENCES workspaces(id),

    -- Visibility (now includes groups)
    visibility VARCHAR(50) DEFAULT 'private',
    -- Examples: 'private', 'workspace', 'group:engineering', 'group:engineering,product'

    -- Explicit shares (for individual users or additional groups)
    shared_with JSONB DEFAULT '[]'::jsonb,
    -- Examples: ["user:alice@example.com", "group:leadership"]

    -- Content...
    source_type VARCHAR(50) NOT NULL,
    title VARCHAR(1000),
    content TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policy with group support
CREATE POLICY "content_visibility_with_groups" ON processed_content
FOR SELECT USING (
    -- Creator always has access
    created_by_user_id = current_user_id()
    OR
    -- Workspace-wide visibility
    (visibility = 'workspace' AND workspace_id IN (
        SELECT workspace_id FROM workspace_memberships
        WHERE user_id = current_user_id() AND status = 'active'
    ))
    OR
    -- Group-based visibility (check if user is in any of the allowed groups)
    (visibility LIKE 'group:%' AND EXISTS (
        SELECT 1 FROM group_memberships gm
        JOIN workspace_groups wg ON gm.group_id = wg.id
        WHERE gm.user_id = current_user_id()
          AND gm.workspace_id = processed_content.workspace_id
          AND visibility LIKE '%' || wg.slug || '%'
    ))
    OR
    -- Explicitly shared with user
    shared_with @> jsonb_build_array('user:' || current_user_email())
    OR
    -- Explicitly shared with user's groups
    EXISTS (
        SELECT 1 FROM group_memberships gm
        JOIN workspace_groups wg ON gm.group_id = wg.id
        WHERE gm.user_id = current_user_id()
          AND shared_with @> jsonb_build_array('group:' || wg.slug)
    )
);
```

#### Permission Matrix

| Action | Owner | Admin | Member | Guest | External |
|--------|-------|-------|--------|-------|----------|
| **Workspace** |
| Delete workspace | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage billing | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage settings | ✅ | ✅ | ❌ | ❌ | ❌ |
| Invite members | ✅ | ✅ | 🔶¹ | ❌ | ❌ |
| Remove members | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Groups** |
| Create groups | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage group members | ✅ | ✅ | 🔶² | ❌ | ❌ |
| Leave group | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Content** |
| Create content | ✅ | ✅ | ✅ | 🔶³ | ❌ |
| Edit own content | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit others' content | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete any content | ✅ | ✅ | ❌ | ❌ | ❌ |
| View workspace content | ✅ | ✅ | ✅ | 🔶⁴ | 🔶⁵ |
| **AI Features** |
| Access workspace AI context | ✅ | ✅ | ✅ | 🔶⁴ | ❌ |
| Train workspace AI | ✅ | ✅ | ✅ | ❌ | ❌ |
| Export AI learnings | ✅ | ❌ | ❌ | ❌ | ❌ |

**Notes:**
- ¹ Members can invite if workspace setting allows
- ² Group leads can manage their own group
- ³ Guests can only create in projects they're assigned to
- ⁴ Guests only see content in their assigned projects/channels
- ⁵ External users only see explicitly shared items

#### Example: Consultant Joining Company Workspace

```
SCENARIO: Greg (consultant) joins Acme Corp workspace

1. INVITATION
   - Acme Admin invites greg@example.com as "Guest"
   - Greg accepts → joins Acme workspace

2. GROUP ASSIGNMENT
   - Admin adds Greg to "contractors" group
   - Admin adds Greg to "project-alpha" group (project-specific)

3. WHAT GREG CAN SEE
   ├─ His personal workspace (all personal data) ✅
   ├─ Acme: Content in "contractors" group ✅
   ├─ Acme: Content in "project-alpha" group ✅
   ├─ Acme: Company-wide announcements ("all-hands") ✅
   ├─ Acme: Engineering docs ("engineering" group) ❌
   └─ Acme: Leadership strategy ("leadership" group) ❌

4. CONTEXT CARD VISIBILITY
   - Acme sees Greg's "work" tier context card
   - Greg controls what's in his "work" tier
   - Greg's "friends" and "private" tiers are hidden from Acme

5. WHEN CONTRACT ENDS
   - Greg leaves Acme workspace
   - Greg keeps: Personal notes, AI learnings, skills gained
   - Greg loses: Access to Acme content, project-alpha materials
   - Acme keeps: Work products Greg created (marked as workspace-owned)
```

### Architectural Patterns Applied

| Pattern | How Flourisha Uses It | Reference |
|---------|----------------------|-----------|
| **User-First Identity** | User is primary entity, workspaces are memberships | GitHub model |
| **Federated Access** | Single identity joins multiple workspaces | Slack Enterprise Grid |
| **Tiered Visibility** | Context cards with public/friends/work/private | Facebook privacy model |
| **Ownership Separation** | User owns portable data, workspace owns work products | GDPR Article 20 |
| **Row-Level Security** | Supabase RLS policies per workspace membership | PostgreSQL RLS |
| **Invitation-Based Growth** | Workspace owners invite members, organic spread | Slack/Discord viral loops |
| **Freemium + Seat-Based** | Personal free, team paid per member | Notion/ClickUp model |

### Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | Current: Single-user with tenant_id | ✅ Working |
| **Phase 2** | Add users table, personal workspace concept | 🔄 Planned |
| **Phase 3** | Multi-workspace memberships, role-based access | 🔄 Planned |
| **Phase 4** | Context cards with tiered visibility | 🔄 Planned |
| **Phase 5** | Data portability, leave workspace workflows | 🔄 Planned |
| **Phase 6** | Billing integration, invitation mechanics | 🔄 Planned |

### Security Considerations

1. **Workspace Isolation**: RLS ensures users only see data in their workspaces
2. **Context Card Privacy**: Tiered visibility prevents over-sharing
3. **Data Portability**: Clear ownership enables clean separation on leave
4. **SSO/SCIM**: Enterprise workspaces can federate identity
5. **Audit Logging**: Track who accessed what in which workspace context

### Comparison: Traditional Multi-Tenant vs Flourisha Multi-Workspace

| Aspect | Traditional Multi-Tenant | Flourisha Multi-Workspace |
|--------|--------------------------|---------------------------|
| **Primary Key** | `tenant_id` | `user_id` + `workspace_id` |
| **User Identity** | Per-tenant | Global, portable |
| **Data Ownership** | Tenant owns all | User owns personal, workspace owns work |
| **Leaving Org** | Lose all data | Take personal data |
| **Multiple Orgs** | Multiple accounts | One account, multiple memberships |
| **AI Context** | Per-tenant AI | Personal AI + workspace context |
| **Billing** | Org pays for users | Workspace pays per seat |
| **Invite Flow** | Admin provisions | Members invite |

---

## Integrations Architecture

> **Key Principle:** Integrations use the best approach for each service - MCP servers for AI-native tooling, Direct API for performance-critical or complex workflows.

### Integration Types

| Type | When to Use | Examples |
|------|-------------|----------|
| **MCP Server** | AI-native tools, dynamic addition, Claude Code integration | Gmail, Slack, Browser automation |
| **Direct API** | High-performance, complex auth, batch processing, existing services | YouTube, Neo4j, Supabase, Google Calendar |
| **Skill Wrapper** | Complex workflows combining multiple tools | `clickup-tasks`, `flourisha-sync`, `research` |

### Integration Status

| Integration | Category | Status | Type | Notes |
|-------------|----------|--------|------|-------|
| **Gmail** | Email | ✅ Working | MCP | OAuth 2.0, label-based ingestion |
| **Outlook** | Email | 🔄 Planned | MCP | Microsoft Graph API |
| **Google Calendar** | Calendar | ✅ Working | Direct API | Schedule integration |
| **Outlook Calendar** | Calendar | 🔄 Planned | MCP | Part of Microsoft Graph |
| **ClickUp** | Project Mgmt | ✅ Working | Skill | Task management, autonomous dev |
| **Google Drive** | Storage | ✅ Working | Skill | Bidirectional sync via rclone |
| **OneDrive** | Storage | 🔄 Planned | MCP | Microsoft Graph API |
| **Slack** | Communication | 🔄 Planned | MCP | Workspace messaging |
| **YouTube** | Content | ✅ Working | Direct API | Playlist processing, transcript extraction |
| **Neo4j** | Graph DB | ✅ Working | Direct API | Knowledge graph via bolt protocol |
| **Supabase** | Database | ✅ Working | Direct API | Vector + relational via SDK |
| **Playwright** | Browser | ✅ Working | MCP | Browser automation |

### ERP Integration Potential

| ERP System | Priority | Integration Approach |
|------------|----------|---------------------|
| **QuickBooks** | High | MCP server via QuickBooks API |
| **Xero** | Medium | MCP server via Xero API |
| **SAP** | Low | MCP server via SAP APIs |
| **NetSuite** | Medium | MCP server via SuiteTalk |
| **Odoo** | High | MCP server via XML-RPC/REST |
| **Salesforce** | High | MCP server via Salesforce APIs |

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FLOURISHA INTEGRATION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FLOURISHA CORE                                                             │
│  │                                                                          │
│  ├─► MCP SERVERS (AI-native, dynamic)                                       │
│  │    ├─► mcp__gmail        (Email)              ✅ Working                 │
│  │    ├─► mcp__outlook      (Email)              🔄 Planned                 │
│  │    ├─► mcp__slack        (Communication)      🔄 Planned                 │
│  │    ├─► mcp__playwright   (Browser)            ✅ Working                 │
│  │    └─► mcp__[new]        (Extensible)         ➕ Dynamic                 │
│  │                                                                          │
│  ├─► DIRECT API (Performance, complex workflows)                            │
│  │    ├─► YouTube API       (Content)            ✅ Working                 │
│  │    ├─► Google Calendar   (Schedule)           ✅ Working                 │
│  │    ├─► Neo4j Bolt        (Graph DB)           ✅ Working                 │
│  │    ├─► Supabase SDK      (Database)           ✅ Working                 │
│  │    └─► [Custom APIs]     (As needed)          ➕ Extensible              │
│  │                                                                          │
│  └─► SKILL WRAPPERS (Complex multi-step workflows)                          │
│       ├─► clickup-tasks     (Project Mgmt)       ✅ Working                 │
│       ├─► flourisha-sync    (Google Drive)       ✅ Working                 │
│       ├─► research          (Multi-agent)        ✅ Working                 │
│       └─► [Custom Skills]   (Orchestration)      ➕ Extensible              │
│                                                                             │
│  CHOOSING INTEGRATION TYPE:                                                 │
│  • MCP: When Claude needs direct tool access (email, browser, chat)         │
│  • Direct API: When performance matters or existing service is mature       │
│  • Skill: When orchestrating multiple tools or complex workflows            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Configuration

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-gmail"],
      "env": { "GMAIL_CREDENTIALS_PATH": "..." }
    },
    "outlook": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-outlook"],
      "env": { "MICROSOFT_CLIENT_ID": "..." }
    },
    "quickbooks": {
      "command": "npx",
      "args": ["-y", "mcp-quickbooks"],
      "env": { "QB_CLIENT_ID": "...", "QB_CLIENT_SECRET": "..." }
    }
  }
}
```

### Adding a New Integration

1. **Find or Build MCP Server**: Check npm for existing `mcp-*` packages or build custom
2. **Configure in settings.json**: Add to `mcpServers` with required environment variables
3. **Update SYSTEM_SPEC.md**: Add to Integration Status table with status
4. **Create Skill (optional)**: Wrap complex workflows in a skill for easier use
5. **Document**: Add to FRONTEND_FEATURE_REGISTRY.md if UI needed

---

## Quick Navigation

| If you want to... | Go to... |
|-------------------|----------|
| **Understand the system** | This file (SYSTEM_SPEC.md) |
| **Build frontend features** | [FRONTEND_FEATURE_REGISTRY.md](FRONTEND_FEATURE_REGISTRY.md) |
| **Understand frontend design** | [FRONTEND_ARCHITECTURE.md](../01f_Flourisha_Projects/flourisha-app/FRONTEND_ARCHITECTURE.md) |
| **Find specific docs** | [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) |
| **Run autonomous development** | [AUTONOMOUS_TASK_SPEC.md](AUTONOMOUS_TASK_SPEC.md) |
| **Quick commands** | [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) |

---

## The Five Pillars Architecture

Flourisha organizes functionality into five pillars representing the flow of information and action:

```
1. INGEST ──► 2. KNOW ──► 3. THINK ──► 4. EXECUTE ──► 5. GROW
   │            │            │             │              │
Content      Knowledge   Strategic     Agentic        System
Ingestion      Hub       Command      Operations    Evolution
```

---

# 1. INGEST (Content Ingestion)

**Purpose:** Bring content from everywhere into Flourisha's knowledge system.

## Features

| Feature | Status | Backend | Documentation |
|---------|--------|---------|---------------|
| YouTube Playlist Processor | Working | `services/youtube_playlist_processor.py` | [YOUTUBE_PLAYLIST_PROCESSOR.md](services/YOUTUBE_PLAYLIST_PROCESSOR.md) |
| YouTube Multi-Channel Manager | Working | `services/youtube_channel_manager.py` | [FRONTEND_FEATURE_REGISTRY.md#12](FRONTEND_FEATURE_REGISTRY.md#12-youtube-multi-channel-manager) |
| Transcript Service (Tor + Whisper) | Working | `services/transcript_service.py` | [TRANSCRIPT_SERVICE.md](services/TRANSCRIPT_SERVICE.md) |
| Document Processor | Working | `services/document_processor.py` | [DOCUMENT_PROCESSOR.md](services/DOCUMENT_PROCESSOR.md) |
| **PDF Ingestion** | Working | `services/document_processor.py` | Claude PDF (primary), Docling (backup) |
| **Spreadsheet Ingestion** | 🔄 Planned | `services/document_processor.py` | CSV, Excel, Google Sheets |
| **Text Document Ingestion** | 🔄 Planned | `services/document_processor.py` | Word, Google Doc, MD, TXT |
| **Meeting Transcript Ingestion** | 🔄 Planned | `services/document_processor.py` | Zoom, Meet, Teams transcripts |
| Knowledge Ingestion Pipeline | Working | `services/knowledge_ingestion_service.py` | [KNOWLEDGE_INGESTION.md](services/KNOWLEDGE_INGESTION.md) |
| Gmail Integration | Working | `services/gmail_service.py` | Skill: `gmail-integration` |
| **Voice Conversations (Limitless)** | 🔄 Planned | - | Limitless pendant recordings |
| **Web Pages (RSS)** | 🔄 Planned | - | RSS feed ingestion |
| **Other Inboxes** | 🔄 Planned | - | iPostal1, 3013, Anderson |
| Flourisha Sync (Google Drive) | Working | Skill: `flourisha-sync` | CORE skill |

## Architecture

```
Document → DocumentProcessor → ExtractionBackend → KnowledgeIngestionService
                                    │                        │
                              ┌─────┴─────┐        ┌─────────┼─────────┐
                              │           │        │         │         │
                           Claude     Docling   Vector    Graph     Whole
                          (Primary)  (Fallback)  Store    Store     Store
```

## PDF Ingestion & Processing

| Priority | Backend | Technology | Use Case |
|----------|---------|------------|----------|
| **Primary** | Claude PDF | Claude's native PDF vision | All PDF ingestion - highest quality extraction |
| **Backup** | Docling | IBM Docling (Docker) | Fallback when Claude unavailable or for batch processing |

**How it works:**
1. PDFs are sent to Claude's PDF vision capabilities first (native multimodal support)
2. Claude extracts text, tables, and structure with semantic understanding
3. If Claude fails or is unavailable, Docling container handles extraction
4. Extracted content flows to KnowledgeIngestionService → three stores

**Docling Status:** Already installed and running in Docker container. See [EXTRACTION_BACKENDS.md](services/EXTRACTION_BACKENDS.md) for configuration.

## Gmail Integration

Privacy-first email ingestion using label-based selection. Only emails explicitly tagged by the user are ingested.

**How it works:**
1. User applies `Flourisha/Unprocessed` label to emails in Gmail
2. Gmail Monitor Worker polls for labeled emails (every 5 minutes)
3. Email body AND attachments are ingested to all three stores
4. Worker moves email to `Flourisha/Processed` label when complete

**Gmail Monitor Worker** (`00_AI_Brain/scripts/gmail_monitor_worker.py`):

| Setting | Value |
|---------|-------|
| **Poll Interval** | 5 minutes (300s) |
| **Watch Label** | `Flourisha/Unprocessed` |
| **Done Label** | `Flourisha/Processed` |
| **Batch Size** | 10 emails per poll |
| **Log File** | `/var/log/flourisha/gmail_monitor.log` |
| **Runs Via** | systemd service |

**Ingestion Flow:**
```
Gmail API → Download email + attachments
    ↓
DocumentProcessor (for attachments)
    ↓
KnowledgeIngestionService → Vector + Graph + Whole stores
    ↓
Mark as Processed (move label)
```

**Configuration (env vars):**
- `GMAIL_MONITOR_LABEL` - Label to watch (default: `Flourisha/Unprocessed`)
- `GMAIL_PROCESSED_LABEL` - Label after processing (default: `Flourisha/Processed`)
- `GMAIL_POLL_INTERVAL` - Seconds between polls (default: `300`)
- `GMAIL_BATCH_SIZE` - Max emails per poll (default: `10`)

## Content Processing Queue

Background worker that processes async content ingestion jobs from the `processing_queue` database table.

**Content Queue Worker** (`00_AI_Brain/scripts/content_queue_worker.py`):

| Setting | Value |
|---------|-------|
| **Poll Interval** | 10 seconds |
| **Queue Table** | `processing_queue` |
| **Max per Poll** | 10 items |
| **Runs Via** | systemd service |

**Supported Job Types:**
- YouTube video processing (transcript extraction, AI summary)
- Playlist monitoring (new video detection)
- Document batch processing

**How it works:**
1. Services add items to `processing_queue` table with status `PENDING`
2. Worker polls table every 10 seconds
3. Processes oldest pending items first
4. Updates status to `COMPLETED` or `FAILED`
5. Results stored in appropriate tables

## Key Files
- `00_AI_Brain/services/youtube_playlist_processor.py`
- `00_AI_Brain/services/document_processor.py`
- `00_AI_Brain/services/knowledge_ingestion_service.py`
- `00_AI_Brain/services/gmail_service.py`
- `00_AI_Brain/scripts/gmail_monitor_worker.py`
- `00_AI_Brain/scripts/content_queue_worker.py`
- `00_AI_Brain/config/youtube_playlist_templates.json`

---

# 2. KNOW (Knowledge Hub)

**Purpose:** Organize and store all knowledge for retrieval and connection.

## Features

| Feature | Status | Backend | Documentation |
|---------|--------|---------|---------------|
| Three-Store Architecture | Working | `services/knowledge_ingestion_service.py` | [OVERVIEW.md](knowledge-stores/OVERVIEW.md) |
| Vector Store (Supabase pgvector) | Working | `services/embeddings_service.py` | [VECTOR_STORE.md](database/VECTOR_STORE.md) |
| Graph Store (Neo4j + Graphiti) | Working | `services/knowledge_graph_service.py` | [GRAPH_STORE.md](knowledge-stores/GRAPH_STORE.md) |
| Document Store (Whole) | Working | `services/document_store.py` | Three-store architecture |
| PARA Organization | Working | `/root/flourisha/01f_*` folders | See Folder Structure |
| **Obsidian Integration** | Working | Google Drive sync | View/edit via Obsidian on desktop |
| **Zettelkasten-Style Notes** | 🔄 Planned | Resources folder | Atomic, interconnected knowledge notes |
| **Chat Session Archive** | 🔄 Planned | Resources folder | Preserved AI conversations as knowledge |
| Memory System (Mem0/oMem) | Planned | - | - |

## Three-Store Architecture

| Store | Technology | Purpose | Data |
|-------|------------|---------|------|
| **Vector** | Supabase pgvector | Semantic search | 1536-dim embeddings |
| **Graph** | Neo4j + Graphiti | Entity relationships | Nodes, edges, properties |
| **Whole** | Supabase raw | Original documents | Full text, metadata |

## Key Files
- `00_AI_Brain/services/knowledge_ingestion_service.py`
- `00_AI_Brain/services/embeddings_service.py`
- `00_AI_Brain/services/knowledge_graph_service.py`

---

# 3. THINK (Strategic Command)

**Purpose:** AI Brain that understands who you are and helps you strategize.

## Features

| Feature | Status | Backend | Documentation |
|---------|--------|---------|---------------|
| Context Card System | Planned | - | [FRONTEND_FEATURE_REGISTRY.md#31](FRONTEND_FEATURE_REGISTRY.md#31-context-card-system) |
| **Ikigai / Purpose Mapping** | 🔄 Planned | Context Card | Discover reason for being, life purpose |
| **Personality Frameworks** | 🔄 Planned | Context Card | Myers-Briggs, Enneagram, StrengthsFinder integration |
| Morning Report | Working | `services/morning_report_service.py` | [MORNING_REPORT.md](services/MORNING_REPORT.md) |
| OKR System | Working | `services/okr_service.py` | [OKR_SYSTEM.md](services/OKR_SYSTEM.md) |
| Energy Tracking | Working | Chrome extension + SMS + Mobile App | [ENERGY_TRACKING.md](services/ENERGY_TRACKING.md) |
| Daily Roadmap | Working | Skill: `daily-roadmap` | Skill definition |
| Personality Profiles | Planned | Neo4j | [FRONTEND_FEATURE_REGISTRY.md](FRONTEND_FEATURE_REGISTRY.md) |
| **Strategy Agents** | 🔄 Planned | `agents/` | AI agents for strategic planning and decision-making |

## Morning Report System

| Setting | Value |
|---------|-------|
| **Delivery Time** | 7:00 AM Pacific |
| **Format** | HTML email via Mailgun |
| **Recipient** | gwasmuth@gmail.com |
| **Sections** | THE ONE THING, Yesterday Recap, Today's Plan, OKR Progress, PARA Updates, Energy Forecast |

## Energy Tracking System

| Feature | Implementation |
|---------|---------------|
| **Capture Method** | Chrome extension popup + SMS prompts |
| **Interval** | Every 90 minutes (8 AM - 6 PM Pacific) |
| **Focus Quality** | Deep / Shallow / Distracted |
| **Energy Scale** | 1-10 with contextual notes |
| **Data Storage** | `energy_tracking` table in Supabase |

## Key Files
- `00_AI_Brain/services/morning_report_service.py`
- `00_AI_Brain/services/okr_service.py`
- `00_AI_Brain/config/morning_report.json`

---

# 4. EXECUTE (Agentic Operations)

**Purpose:** Agents and skills that execute work on your behalf.

## Features

| Feature | Status | Backend | Documentation |
|---------|--------|---------|---------------|
| Skills System | Working | `~/.claude/skills/` | 27 skills available |
| Specialized Agents | Working | `agents/` | researcher, engineer, designer, pentester, architect |
| ClickUp Autonomous Agent | Working | `agents/clickup-autonomous/` | [AUTONOMOUS_TASK_SPEC.md](AUTONOMOUS_TASK_SPEC.md) |
| **Long-Running Agent Harness** | Working | `agents/clickup-autonomous/` | Autonomous multi-day task execution |
| A2A Protocol | Implemented | `a2a/registry/` | [a2a/overview.md](a2a/overview.md) |
| Hook System | Working | `~/.claude/settings.json` | CORE skill |
| Fabric Prompts (242+) | Working | Skill: `fabric` | Skill definition |
| ClickUp Integration | Working | Skill: `clickup-tasks` | Skill definition |
| Research Agents | Working | Skill: `research` | Multi-agent parallel research |

## Skills Architecture

### AI-Agnostic Symlinks

Skills are stored in Flourisha for Google Drive sync and Obsidian access, with symlinks for AI vendor compatibility:

| Location | Purpose |
|----------|---------|
| `/root/flourisha/00_AI_Brain/skills/` | **Canonical location** (syncs to Google Drive) |
| `/root/.claude/skills/` | Symlink → canonical location |

**Benefits:**
- Single source of truth in Flourisha
- Edit skills in Obsidian on any device
- Automatic Google Drive backup/versioning
- Future AI vendor support (Gemini, etc.) via additional symlinks

### Skill Directory Structure

```
skill-name/
├── SKILL.md          # Required: Definition with frontmatter
├── workflows/        # Required: At least one workflow
│   ├── primary.md
│   └── advanced.md
├── assets/           # Optional: Templates, resources
├── examples/         # Recommended: Example outputs
└── scripts/          # Optional: Helper scripts
```

**Minimum Required:**
- `SKILL.md` with frontmatter (name, description, USE WHEN triggers)
- `workflows/` with at least one workflow file

### Progressive Disclosure (3-Tier PAI Pattern)

Skills load progressively to minimize context usage:

| Tier | Content | Size | When Loaded |
|------|---------|------|-------------|
| **Tier 1: Metadata** | SKILL.md frontmatter (name, description, triggers) | ~100 tokens | Startup (routing decisions) |
| **Tier 2: Instructions** | SKILL.md body (how to use, workflow list) | ~2000 tokens | When skill is triggered |
| **Tier 3: Resources** | workflows/, assets/, examples/ subdirectories | 500-2000 tokens each | On-demand as needed |

**Flow:**
1. User request → Match against Tier 1 metadata
2. Skill triggered → Load Tier 2 instructions
3. Workflow executed → Load specific Tier 3 resources

## Agent Types

**Research Agents:**
- `perplexity-researcher` - Real-time web research
- `claude-researcher` - Deep analysis and synthesis
- `gemini-researcher` - Multi-perspective exploration
- `research` skill - Orchestrates Quick/Standard/Extensive modes

**Engineering Agents:**
- `engineer` - General software development
- `architect` - System design and architecture
- `pentester` - Security testing and vulnerability assessment

**Content & Specialist Agents:**
- `designer` - UI/UX and visual design
- Writer/Editor - Content creation (via Fabric patterns)

## Agent Factory Pattern

Temporal agents created for specific, time-bound tasks:
```
agent_Purpose_YYYYMMDD
```
Example: `agent_CompetitorAnalysis_20260115`

See [AGENT_FACTORY.md](services/AGENT_FACTORY.md) for lifecycle management.

## Automation Schedule (Cron Jobs)

All times in **Pacific Time**.

| Time (PT) | Automation | Script |
|-----------|------------|--------|
| Every 15 min | Flourisha Sync | `~/.claude/scripts/flourisha-sync-cron.sh` |
| 2:00 AM | Full Backup | `/root/backups/full_backup.sh` |
| 6:00 AM | Security Check | `/usr/local/bin/security-check.sh` |
| 7:00 AM | Morning Report | `scripts/morning-report-generator.py` |
| Every 4 hours | PARA Analyzer | `scripts/para-analyzer.py` |
| Every hour | Sandbox Cleanup | `scripts/cleanup-old-sandboxes.sh` |

## Key Files
- `00_AI_Brain/agents/` - Agent definitions
- `00_AI_Brain/skills/` - Skill definitions (symlinked to ~/.claude/skills/)
- `00_AI_Brain/a2a/registry/` - A2A protocol registry

---

# 5. GROW (System Evolution)

**Purpose:** Continuous improvement through feedback loops and infrastructure.

## Features

| Feature | Status | Backend | Documentation |
|---------|--------|---------|---------------|
| Extraction Feedback System | Working | `services/extraction_feedback_service.py` | Database tables ready |
| Extraction Backends | Working | `services/extraction_backends/` | [EXTRACTION_BACKENDS.md](services/EXTRACTION_BACKENDS.md) |
| Voice System (ElevenLabs) | Working | Port 8888 | CORE skill voice IDs |
| System Monitoring (Netdata) | Working | `http://100.66.28.67:19999` | Tailscale access |
| Uptime Monitoring (Uptime Kuma) | Working | `http://100.66.28.67:3001` | Tailscale access |
| Playwright MCP (Browser) | Working | MCP server | Browser automation |
| Docker Sandboxes | Working | Skill: `docker-sandbox` | Phase 2 complete |
| Agent Observability | Working | Skill: `agent-observability` | Track agent performance |
| **Claude Agent SDK** | 🔄 Planned | - | Build custom agents with Anthropic SDK |

## Feedback Loop Types

How Flourisha learns and evolves over time:

| Loop Type | Description | Mechanism |
|-----------|-------------|-----------|
| **Updated Documentation** | System docs improve from usage | Auto-capture learnings to SYSTEM_SPEC |
| **New Skill Patterns** | New skills emerge from repeated tasks | Skill creation from successful workflows |
| **Learned Behaviors** | Preferences refined over time | Context Card updates, Memory (oMem) |
| **Enhanced Context** | Knowledge graph grows richer | Entity extraction, relationship mapping |

## Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| **Reliability** | System uptime | 99.5%+ |
| **Reliability** | Morning report delivery | 95%+ on-time |
| **Reliability** | Energy tracking capture | 80%+ compliance |
| **Performance** | RAG query latency | < 2 seconds |
| **Performance** | Morning report generation | < 30 seconds |
| **Performance** | Database query avg | < 100ms |
| **Quality** | Knowledge ingestion success | 95%+ |
| **Quality** | Agent execution success | 90%+ |

## Key Files
- `00_AI_Brain/services/extraction_feedback_service.py`
- `00_AI_Brain/services/extraction_backends/`

---

## Technology Stack

### Backend & Data
| Category | Technology | Purpose |
|----------|------------|---------|
| **Database** | Supabase (PostgreSQL + pgvector) | Primary data store + vector embeddings |
| **Knowledge Graph** | Neo4j + Graphiti | Entity relationships, context graph |
| **AI Models** | Claude (Sonnet/Opus), OpenAI | LLM responses, embeddings |
| **AI Framework** | Pydantic AI | Structured agent development |
| **Email** | Mailgun | HTML morning report delivery |
| **SMS** | Telnyx | Energy tracking prompts |
| **Calendar** | Google Calendar API | Schedule integration |
| **Hosting** | Contabo VPS  IP Address: 66.94.121.10 | Server infrastructure (Ubuntu 22.04) |
| **Orchestration** | systemd + cron | Service management |
| **Sync** | rclone (Google Drive) | Obsidian/multi-device access |

### Frontend Development (Web)
| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | Next.js 14+ | React + API routes + SSR |
| **Styling** | Chakra UI | Accessible component library with built-in theming |
| **Animation** | GSAP | Production-grade motion and transitions |
| **State** | TanStack Query (React Query) | Server state management |
| **Forms** | React Hook Form + Zod | Type-safe form validation |
| **Charts** | Recharts | OKR progress, energy trends |
| **Graph Viz** | react-force-graph | Knowledge graph visualization |
| **Auth** | Firebase Auth | OAuth (Google), Email/Password, JWT tokens |
| **Type Safety** | TypeScript | Static typing |

### Mobile Development (iOS & Android)
| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | React Native + Expo | Cross-platform native apps |
| **Navigation** | Expo Router | File-based routing (mirrors Next.js) |
| **Styling** | NativeWind (Tailwind) | Consistent styling across platforms |
| **State** | TanStack Query | Same as web (shared logic) |
| **Camera** | expo-camera | Photo capture for document/idea ingestion |
| **Audio Recording** | expo-av | Voice memo recording |
| **Speech-to-Text** | Deepgram / AssemblyAI | Real-time transcription + diarization |
| **Text-to-Speech** | ElevenLabs | Natural voice responses |
| **Push Notifications** | Expo Notifications | Native push via APNs/FCM |
| **Auth** | Firebase Auth | Same auth as web |

### Voice & Audio Services
| Category | Technology | Purpose |
|----------|------------|---------|
| **Speech-to-Text** | Deepgram | Real-time transcription, speaker diarization |
| **Text-to-Speech** | ElevenLabs | Natural AI voice responses |
| **Audio Processing** | expo-av | Recording, playback on mobile |
| **WebRTC** | LiveKit (optional) | Real-time voice conversations |

### Code Sharing Strategy
```
flourisha/
├── apps/
│   ├── web/           # Next.js web app
│   └── mobile/        # Expo React Native app
├── packages/
│   ├── shared/        # Shared TypeScript types, utils
│   ├── api-client/    # Shared API client (TanStack Query hooks)
│   └── ui/            # Shared component logic (where possible)
```

**Shared between Web & Mobile:**
- TypeScript types and Zod schemas
- API client and TanStack Query hooks
- Business logic and utilities
- Supabase client configuration

**Platform-Specific:**
- UI components (Chakra UI for web, NativeWind for mobile)
- Navigation (Next.js routing vs Expo Router)
- Native features (camera, audio, push notifications)

---

## Authentication Architecture

> **Key Design Decision:** Firebase handles user authentication (identity), Supabase handles data storage (PostgreSQL). This separation provides flexibility and leverages each platform's strengths.

### Authentication Flow

```
User Login → Firebase Auth → JWT Token → Backend validates JWT → Supabase RLS enforces access
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **User Authentication** | Firebase Auth | Email/Password, Google OAuth |
| **JWT Verification** | Firebase Public Keys | Backend validates tokens without service account |
| **Deep Linking** | Firebase Dynamic Links | 🔄 Planned - Universal links from web/email into app |
| **Database** | Supabase PostgreSQL | All application data with RLS policies |
| **Authorization** | Supabase RLS | Row-level security validates JWT claims |

### Firebase Configuration

| Setting | Value |
|---------|-------|
| **Project ID** | `flourisha-d959a` |
| **Auth Methods** | Email/Password, Google OAuth |
| **Custom Claims** | `tenant_id`, `groups`, `role` |
| **JWT Verification** | Public key validation (no service account needed) |
| **Dynamic Links** | 🔄 Planned - Deep linking into mobile app |

### Deep Linking (Planned)

Firebase Dynamic Links enable seamless user journeys from any surface into the app:

| Use Case | Link Example | Destination |
|----------|--------------|-------------|
| **Morning Report email** | `flourisha.page.link/report/2025-12-18` | Opens report in app |
| **OKR check-in reminder** | `flourisha.page.link/okr/q1-2025` | Opens OKR dashboard |
| **Energy tracking SMS** | `flourisha.page.link/energy` | Opens energy input |
| **Shared knowledge item** | `flourisha.page.link/knowledge/abc123` | Opens specific content |
| **Invitation link** | `flourisha.page.link/invite/workspace-id` | Workspace onboarding |

**How it works:**
1. Links work on web (redirect to app store if not installed) and in-app
2. Context preserved through install - user lands on intended screen
3. Analytics on link performance via Firebase Console

### Key Auth Files

- `00_AI_Brain/auth/firebase_auth.py` - JWT verification implementation
- `00_AI_Brain/documentation/security/OAUTH_CREDENTIALS.md` - Credential management

---

## Infrastructure

### Core Services
| Service | Access | Purpose |
|---------|--------|---------|
| Firebase | `flourisha-d959a` project | Auth (working), Dynamic Links (planned) |
| Supabase | Cloud | PostgreSQL + pgvector (database only) |
| Neo4j | `bolt://neo4j.leadingai.info:7687` | Graph database |
| Tor Proxy | `socks5://127.0.0.1:9050` | YouTube transcript fetching |
| Voice Server | `localhost:8888` | ElevenLabs TTS |
| Docling | Docker container | OCR/document extraction |

### Server Administration
| Service | Access | Purpose |
|---------|--------|---------|
| Portainer | `https://portainer.leadingai.info` | Docker container management UI |
| File Browser | `https://files.leadingai.info` | Web-based file management |
| Tailscale | `100.66.28.67` | Secure mesh VPN |
| Cockpit | `https://cockpit.leadingai.info` | Server administration UI |

### Monitoring & Security
| Service | Access | Purpose |
|---------|--------|---------|
| Netdata | `http://100.66.28.67:19999` | Real-time system monitoring |
| Uptime Kuma | `http://100.66.28.67:3001` | Service uptime monitoring |
| Traefik | Reverse proxy | SSL termination, routing |
| Fail2ban | System service | Intrusion prevention |
| UFW | System service | Firewall management |

---

## MyRemoteLender Migration (Airtable + Make.com → Supabase)

**Status:** Phase 1 Complete (tables deployed with data)

### Overview

Migration of the MyRemoteLender universal document management system from Airtable + Make.com to Supabase + Knowledge Graph.

### Migration Phases

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| **Phase 1** | Foundation | ✅ Complete | Supabase tables mirroring Airtable structure |
| **Phase 2** | Knowledge Graph | 🔄 Partial | Connect Supabase to Neo4j ontology |
| **Phase 3** | Make.com Migration | ⏳ Pending | Move automations from Airtable to Supabase |
| **Phase 4** | Schema.org Alignment | ⏳ Pending | Standardize naming to Schema.org conventions |

### MRL Tables (Supabase)

All tables use `mrl_` prefix. **17 tables deployed with 776 rows.**

| Table | Rows | Schema.org Mapping |
|-------|------|-------------------|
| `mrl_documents` | 39 | DigitalDocument |
| `mrl_doc_types` | 250 | flourisha:DocumentType |
| `mrl_conditions` | 45 | flourisha:LoanCondition |
| `mrl_companies` | 38 | Organization |
| `mrl_company_types` | 48 | - |
| `mrl_contacts` | 8 | Person |
| `mrl_roles` | 130 | - |
| `mrl_loans` | 60 | LoanOrCredit |
| `mrl_properties` | 9 | RealEstateProperty |
| `mrl_agreements` | 14 | Contract |
| `mrl_accounts` | 2 | - |
| `mrl_account_users` | 11 | - |
| `mrl_categories` | 11 | - |
| `mrl_property_components` | 27 | - |
| `mrl_issue_items` | 77 | - |
| `mrl_repairs` | 1 | - |
| `mrl_messages` | 6 | - |

### Key Constraint

> **Make.com scenarios reference specific Airtable field IDs** - cannot rename or restructure until scenarios are migrated.

### Schema.org URIs (Phase 4)

| Entity | Schema.org Type | URI |
|--------|-----------------|-----|
| Documents | DigitalDocument | https://schema.org/DigitalDocument |
| Companies | Organization | https://schema.org/Organization |
| Contacts | Person | https://schema.org/Person |
| Properties | RealEstateProperty | https://schema.org/RealEstateProperty |
| Agreements | Contract | https://schema.org/Contract |
| Loans | LoanOrCredit | https://schema.org/LoanOrCredit |
| Conditions | (custom) | flourisha:LoanCondition |
| Doc Types | (custom) | flourisha:DocumentType |

### Key Files

| File | Purpose |
|------|---------|
| `migrations/airtable_schema.json` | Full Airtable schema export (458 fields) |
| `migrations/mrl_tables.sql` | Supabase table creation SQL (165KB) |
| `services/ontology.py` | Graphiti entity/edge type definitions |

### Remaining Work

**Phase 2 (Knowledge Graph):**
- [ ] Update ontology.py with MRL-specific entities (Loan, Condition, Agreement)
- [ ] Map Airtable relationships to Graphiti edge types
- [ ] Create ingestion pipeline: Supabase MRL tables → Neo4j

**Phase 3 (Make.com Migration):**
- [ ] Inventory all Make.com scenarios using Airtable
- [ ] Create Supabase-based replacement for each scenario
- [ ] Parallel testing and cutover

**Phase 4 (Schema.org Alignment):**
- [ ] Rename Supabase columns to Schema.org conventions
- [ ] Add Schema.org type annotations to ontology
- [ ] Document final schema with URIs

---

## PARA Folder Structure

```
/root/flourisha/                      # Google Drive sync + Obsidian
├── 00_AI_Brain/                      # AI INFRASTRUCTURE
│   ├── documentation/               # All system docs
│   │   └── SYSTEM_SPEC.md          # THIS FILE
│   ├── services/                    # Python services
│   ├── skills/                      # PAI Skills (symlinked)
│   ├── agents/                      # Agent definitions
│   ├── scripts/                     # Automation scripts
│   └── config/                      # Configuration files
│
├── 01f_Flourisha_Projects/          # PARA: Active projects
├── 02f_Flourisha_Areas/             # PARA: Ongoing responsibilities
├── 03f_Flourisha_Resources/         # PARA: Reference materials
└── 04f_Flourisha_Archives/          # PARA: Completed items
```

---

## Autonomous Development

Flourisha can be built autonomously using the ClickUp Coding Agent Harness.

**Quick Start:**
```bash
cd /root/flourisha/00_AI_Brain/agents/clickup-autonomous
source ~/.claude/.env
python run_autonomous_agent.py --project flourisha --project-dir /root/flourisha/00_AI_Brain/api
```

**Key Files:**
- `documentation/AUTONOMOUS_TASK_SPEC.md` - Task specifications (organized by Five Pillars)
- `agents/clickup-autonomous/prompts/flourisha_spec.txt` - Detailed project spec
- `agents/clickup-autonomous/prompts/flourisha_initializer_prompt.md` - Agent initialization
- `agents/clickup-autonomous/prompts/flourisha_coding_prompt.md` - Coding agent instructions

**ClickUp Setup:**
- List ID: `901112685055` (Flourisha API Backend)
- META Task ID: `868grh6hr`
- Space ID: `14700061` (Project Central)

---

## Autonomous Update Protocol

> **CRITICAL:** When an autonomous agent completes a task, it MUST update this SYSTEM_SPEC.md to reflect the new status. This prevents duplicate work and keeps the spec as the source of truth.

### Status Indicators

| Status | Meaning | Use When |
|--------|---------|----------|
| ✅ Working | Feature is implemented and functional | Code exists, tested, in production |
| 🔄 Planned | Feature is designed but not built | Spec exists, no code yet |
| 🚧 In Progress | Actively being developed | Work has started, not complete |
| ⚠️ Broken | Was working, now has issues | Needs debugging/fixing |
| ❌ Deprecated | No longer supported | Replaced or removed |

### Update Protocol for Autonomous Agents

When completing ANY task, the agent MUST:

```
1. READ SYSTEM_SPEC.md FIRST
   - Check if the feature already has a status
   - Understand current state before starting work
   - DON'T duplicate work that's already ✅ Working

2. DURING WORK
   - If starting a new feature: Change status to 🚧 In Progress
   - If fixing a broken feature: Keep as ⚠️ Broken until fixed

3. AFTER COMPLETING WORK
   - Change status to ✅ Working
   - Update any notes/documentation columns
   - Add completion date in notes if helpful
   - Update FRONTEND_FEATURE_REGISTRY.md if UI-related

4. IF TASK FAILS
   - Change status to ⚠️ Broken with error note
   - Document what went wrong for next agent
```

### Example: Completing a Feature

**Before (in SYSTEM_SPEC.md):**
```markdown
| Outlook | Email | 🔄 Planned | `outlook-mcp` | Microsoft Graph API |
```

**After agent completes work:**
```markdown
| Outlook | Email | ✅ Working | `outlook-mcp` | Microsoft Graph API, completed 2025-12-18 |
```

### Files to Update on Completion

| What Changed | Update These Files |
|--------------|-------------------|
| Backend service | SYSTEM_SPEC.md (feature table), service doc in `services/*.md` |
| Integration | SYSTEM_SPEC.md (Integrations table), Integration Configuration section |
| Frontend feature | FRONTEND_FEATURE_REGISTRY.md (feature spec + checkbox) |
| Database schema | DATABASE_SCHEMA.md, SYSTEM_SPEC.md if major |
| New skill | SYSTEM_SPEC.md (Execute section), skill SKILL.md |

### Preventing Duplicate Work

Autonomous agents should:

1. **Always read SYSTEM_SPEC.md** at session start
2. **Check status before starting** any feature work
3. **Skip ✅ Working features** unless explicitly asked to modify
4. **Claim work** by setting 🚧 In Progress before starting
5. **Update immediately** on completion, not later

### Status Update Commands

For autonomous agents, use these patterns:

```python
# Pattern for updating SYSTEM_SPEC.md status
# Find: | Feature Name | Category | 🔄 Planned |
# Replace: | Feature Name | Category | ✅ Working |

# Always update the "Last Updated" date at top of file
# *Last Updated: YYYY-MM-DD*
```

---

## Document Hierarchy

```
SYSTEM_SPEC.md (this file) ← THE canonical reference
    │
    ├── FRONTEND_FEATURE_REGISTRY.md (detailed frontend specs)
    │
    ├── DOCUMENTATION_MAP.md (index to all docs)
    │   ├── services/*.md
    │   ├── database/*.md
    │   ├── knowledge-stores/*.md
    │   └── guides/*.md
    │
    ├── AUTONOMOUS_TASK_SPEC.md (ClickUp tasks by Five Pillars)
    │
    └── plans/ (future enhancement plans)
        ├── document-intelligence-pydantic-ai.md (Pydantic AI doc extraction)
        └── zippy-humming-allen.md (Firebase Auth doc updates)
```

### Active Enhancement Plans

| Plan | Purpose | Status |
|------|---------|--------|
| [document-intelligence-pydantic-ai.md](plans/document-intelligence-pydantic-ai.md) | Advanced document extraction using Pydantic AI agents | Future |
| [zippy-humming-allen.md](plans/zippy-humming-allen.md) | Update SYSTEM_SPEC with Firebase Auth details | Pending |

---

## Contact & Identity

- **Name:** Flourisha
- **Role:** AI chief of staff
- **User:** Greg Wasmuth (San Diego, CA - Pacific Time)
- **Email:** gwasmuth@gmail.com

---

*This is THE canonical system specification. Autonomous agents should start here.*

*For detailed frontend implementation, see [FRONTEND_FEATURE_REGISTRY.md](FRONTEND_FEATURE_REGISTRY.md)*

*For document index, see [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)*
