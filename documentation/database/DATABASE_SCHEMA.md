# Database Schema

Complete reference for the AI Brain database schema in Supabase (PostgreSQL).

## SQL Files Location

All schema definitions are in `/root/flourisha/00_AI_Brain/database/`:

| File | Description |
|------|-------------|
| `01_content_intelligence_schema.sql` | Core tables with multi-tenant RLS |
| `02_add_embeddings.sql` | pgvector embedding support |
| `match_documents_function.sql` | Vector similarity search function |
| `functions/` | Additional SQL functions |
| `schemas/` | Schema definitions |

## Table Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Supabase (PostgreSQL)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CORE TABLES                                                                │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐           │
│  │     tenants     │   │  tenant_users   │   │    projects     │           │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘           │
│                                                                             │
│  CONTENT TABLES                                                             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐           │
│  │ processed_      │   │  input_sources  │   │   processing    │           │
│  │   content       │   │                 │   │     _queue      │           │
│  │  + embedding    │   │                 │   │                 │           │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘           │
│                                                                             │
│  YOUTUBE TABLES                                                             │
│  ┌─────────────────┐                                                       │
│  │   youtube_      │                                                       │
│  │ subscriptions   │                                                       │
│  └─────────────────┘                                                       │
│                                                                             │
│  Extension: pgvector (vector similarity search)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Table Schemas

### processed_content
Main content storage table with embeddings.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | TEXT | Multi-tenant isolation |
| `tenant_user_id` | TEXT | User who owns content |
| `created_by_user_id` | TEXT | User who created |
| `project_id` | UUID | FK to projects |
| `visibility` | VARCHAR(50) | 'private', 'tenant', or 'group:X' |
| `shared_with` | JSONB | Array of groups/users |
| `source_type` | VARCHAR(50) | Content source type |
| `source_id` | VARCHAR(500) | External ID |
| `title` | VARCHAR(1000) | Content title |
| `raw_content` | TEXT | Original content |
| `transcript` | TEXT | Transcript (if audio/video) |
| `summary` | TEXT | AI-generated summary |
| `key_insights` | JSONB | Extracted insights |
| `tags` | JSONB | Content tags |
| `embedding` | vector(1536) | pgvector embedding |
| `embedding_model` | TEXT | Model used |
| `vector_id` | TEXT | External vector DB ID |
| `graph_node_id` | TEXT | Neo4j node ID |
| `processing_status` | VARCHAR(50) | 'pending', 'processing', 'completed', 'failed' |

### projects
Project organization.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | TEXT | Multi-tenant isolation |
| `name` | VARCHAR(255) | Project name |
| `description` | TEXT | Project description |
| `youtube_playlist_id` | VARCHAR(255) | Linked playlist |
| `tech_stack` | JSONB | Tech configuration |
| `visibility_defaults` | JSONB | Default visibility rules |

### input_sources
Content input sources (YouTube, Limitless, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | TEXT | Multi-tenant isolation |
| `project_id` | UUID | FK to projects |
| `source_type` | VARCHAR(50) | 'youtube', 'limitless', 'meeting', 'manual', 'voice_note' |
| `source_identifier` | VARCHAR(500) | Playlist ID, channel ID, etc. |
| `config` | JSONB | Source configuration |
| `is_active` | BOOLEAN | Active status |

### processing_queue
Async processing queue.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | TEXT | Multi-tenant isolation |
| `content_id` | UUID | FK to processed_content |
| `priority` | INTEGER | 1-10 (higher = more urgent) |
| `retry_count` | INTEGER | Current retry count |
| `status` | VARCHAR(50) | 'queued', 'processing', 'completed', 'failed' |

### youtube_subscriptions
YouTube channel/playlist subscriptions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | TEXT | Multi-tenant isolation |
| `project_id` | UUID | FK to projects |
| `channel_id` | VARCHAR(255) | YouTube channel ID |
| `playlist_id` | VARCHAR(255) | YouTube playlist ID |
| `auto_process` | BOOLEAN | Auto-process new videos |

## Row-Level Security (RLS)

All tables have RLS enabled for multi-tenant security:

```sql
-- Content visibility policy
CREATE POLICY "content_visibility_control"
ON processed_content
FOR SELECT
USING (
    -- User owns the content
    created_by_user_id = (jwt->>'sub')
    OR
    -- Content is tenant-wide
    (visibility = 'tenant' AND tenant_id = (jwt->>'tenant_id'))
    OR
    -- User is in shared group
    user_groups && shared_with_groups
);
```

## Vector Search

### Embedding Configuration
- **Model**: text-embedding-3-small (OpenAI)
- **Dimensions**: 1536
- **Index**: IVFFlat with cosine similarity

### Search Function
```sql
-- Search by embedding similarity
SELECT * FROM search_content_by_embedding(
    query_embedding := $1,
    match_tenant_id := 'default',
    match_threshold := 0.7,
    match_count := 10
);
```

### Python Usage
```python
from services.knowledge_ingestion_service import get_ingestion_service

service = get_ingestion_service()
results = await service.query_knowledge(
    query="blood pressure",
    search_vector=True
)
```

## Indexes

Key indexes for performance:

| Table | Index | Purpose |
|-------|-------|---------|
| processed_content | `idx_content_tenant_user` | Tenant+user queries |
| processed_content | `idx_content_visibility` | Visibility filtering |
| processed_content | `idx_content_tags` | Tag search (GIN) |
| processed_content | `embedding_idx` | Vector similarity (IVFFlat) |
| projects | `idx_projects_tenant` | Tenant isolation |
| processing_queue | `idx_queue_status_priority` | Queue processing |

## Migrations

To apply schema changes:

1. **Via Supabase Dashboard**: SQL Editor → paste SQL
2. **Via CLI**:
```bash
supabase db push
```

## Important Notes

1. **Multi-Tenant**: All queries automatically filtered by `tenant_id`
2. **RLS Required**: Direct database access requires JWT with tenant claim
3. **Embedding Size**: 1536 dimensions (text-embedding-3-small)
4. **pgvector**: Extension must be enabled in Supabase

## New Tables (Phase 1)

The following tables are being added to support the Flourisha AI Brain system.

### energy_tracking

Real-time energy and focus quality tracking for productivity optimization.

```sql
CREATE TABLE energy_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Tracking Data
    timestamp TIMESTAMPTZ NOT NULL,
    energy_level INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    focus_quality VARCHAR(20) NOT NULL CHECK (focus_quality IN ('deep', 'shallow', 'distracted')),

    -- Context
    current_task TEXT,
    source VARCHAR(20) NOT NULL CHECK (source IN ('chrome_extension', 'sms', 'manual')),

    -- Optional metadata
    location VARCHAR(100),
    notes TEXT,

    -- RLS
    CONSTRAINT energy_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE energy_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_energy_access"
ON energy_tracking
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_energy_user_time ON energy_tracking(user_id, timestamp DESC);
CREATE INDEX idx_energy_tenant ON energy_tracking(tenant_id);
CREATE INDEX idx_energy_timestamp ON energy_tracking(timestamp DESC);
CREATE INDEX idx_energy_user_date ON energy_tracking(user_id, DATE(timestamp));
```

**Usage:**
- Chrome extension captures energy/focus every 90 minutes
- SMS fallback via Telnyx for mobile tracking
- Powers energy forecasting in morning reports
- Enables task-to-energy matching

**Related Documentation:** [ENERGY_TRACKING.md](../services/ENERGY_TRACKING.md)

### okr_tracking

Quarterly OKR (Objectives and Key Results) tracking with progress measurement.

```sql
CREATE TABLE okr_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- OKR Structure
    quarter VARCHAR(10) NOT NULL,  -- e.g., 'Q1 2026'
    objective_number INTEGER NOT NULL,
    objective TEXT NOT NULL,
    objective_description TEXT,

    key_result_number VARCHAR(10) NOT NULL,  -- e.g., '1.1'
    key_result TEXT NOT NULL,
    key_result_type VARCHAR(20) NOT NULL,  -- 'percentage', 'count', 'binary', 'average'

    -- Targets and Progress
    target_value NUMERIC NOT NULL,
    current_value NUMERIC DEFAULT 0,
    progress_percentage NUMERIC GENERATED ALWAYS AS (
        CASE
            WHEN target_value > 0 THEN (current_value / target_value * 100)
            ELSE 0
        END
    ) STORED,

    -- Metadata
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'completed', 'abandoned'
    owner TEXT DEFAULT 'gwasmuth@gmail.com',
    measurement_frequency VARCHAR(20) DEFAULT 'weekly',

    -- Risk Management
    blockers JSONB DEFAULT '[]',
    risks JSONB DEFAULT '[]',
    notes TEXT,

    -- RLS
    CONSTRAINT okr_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE okr_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_okr_access"
ON okr_tracking
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_okr_quarter ON okr_tracking(quarter);
CREATE INDEX idx_okr_tenant ON okr_tracking(tenant_id);
CREATE INDEX idx_okr_status ON okr_tracking(status);
CREATE UNIQUE INDEX idx_okr_unique ON okr_tracking(tenant_id, quarter, key_result_number);
```

**Companion Table: okr_measurements**

```sql
CREATE TABLE okr_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    okr_id UUID NOT NULL REFERENCES okr_tracking(id) ON DELETE CASCADE,
    measured_at TIMESTAMPTZ DEFAULT NOW(),

    -- Measurement Data
    measured_value NUMERIC NOT NULL,
    measurement_type VARCHAR(20),  -- 'daily', 'weekly', 'monthly', 'manual'
    measured_by TEXT,

    -- Context
    notes TEXT,
    data_source VARCHAR(100),

    -- RLS
    CONSTRAINT measurement_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE okr_measurements ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_measurement_access"
ON okr_measurements
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_measurement_okr ON okr_measurements(okr_id);
CREATE INDEX idx_measurement_date ON okr_measurements(measured_at DESC);
```

**Usage:**
- Quarterly OKR tracking (4 objectives per quarter)
- Weekly measurement schedule (Monday 8 AM)
- Morning report integration for daily visibility
- Progress calculation and status determination

**Related Documentation:** [OKR_SYSTEM.md](../services/OKR_SYSTEM.md)

### personality_profiles (Phase 3 - Neo4j)

Personality profiles for saved contacts stored in Neo4j knowledge graph.

**Note:** This table is implemented in Neo4j (not Supabase) as part of Phase 3. It leverages the graph structure for relationship mapping.

**Neo4j Schema:**

```cypher
// Person node with personality profile
CREATE (p:Person {
    id: randomUUID(),
    email: 'contact@example.com',
    name: 'Contact Name',
    created_at: datetime(),
    updated_at: datetime()
})

// Personality profile properties
SET p.communication_style = 'direct'  // 'direct', 'collaborative', 'formal', 'casual'
SET p.response_preference = 'concise'  // 'concise', 'detailed', 'conversational'
SET p.decision_making = 'analytical'  // 'analytical', 'intuitive', 'collaborative'
SET p.work_style = 'structured'  // 'structured', 'flexible', 'spontaneous'

// Personality traits (JSONB-equivalent as map)
SET p.traits = {
    openness: 7,
    conscientiousness: 8,
    extraversion: 5,
    agreeableness: 8,
    neuroticism: 3
}

// Context and history
SET p.interaction_history = []  // Array of interaction summaries
SET p.topics_of_interest = ['AI', 'productivity', 'health']
SET p.preferred_contact_times = ['morning', 'early-afternoon']

// Relationships
CREATE (p)-[:WORKS_AT]->(org:Organization {name: 'Company Name'})
CREATE (p)-[:INTERESTED_IN]->(topic:Topic {name: 'AI'})
CREATE (p)-[:PREFERS_CHANNEL]->(channel:Channel {name: 'email'})
```

**Usage:**
- Enhanced email response generation with personality context
- Communication style adaptation
- Relationship context enrichment
- Department 2 (Knowledge Intelligence) integration

**Query Examples:**

```cypher
// Get personality profile for email recipient
MATCH (p:Person {email: $email})
RETURN p.communication_style, p.response_preference, p.traits

// Find similar personalities
MATCH (p1:Person {email: $email})-[:SIMILAR_TO]->(p2:Person)
RETURN p2

// Get interaction history
MATCH (p:Person {email: $email})
RETURN p.interaction_history ORDER BY timestamp DESC LIMIT 10
```

**Related Documentation:** Knowledge Stores documentation (Phase 3)

### agent_feedback (Phase 4)

Agent execution feedback for continuous improvement and learning.

```sql
CREATE TABLE agent_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Agent Identification
    agent_id TEXT NOT NULL,  -- e.g., 'agent_CompetitorAnalysis_20260115'
    agent_type VARCHAR(50) NOT NULL,  -- 'research', 'content', 'engineering', 'email'
    execution_date TIMESTAMPTZ NOT NULL,

    -- Execution Data
    task_description TEXT NOT NULL,
    execution_duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL,  -- 'success', 'partial', 'failed'

    -- Outcomes
    outcome_summary TEXT,
    deliverables JSONB,  -- Array of produced artifacts
    errors JSONB DEFAULT '[]',  -- Array of errors encountered

    -- Quality Assessment
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 10),
    accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 10),
    completeness_rating INTEGER CHECK (completeness_rating BETWEEN 1 AND 10),

    -- Feedback
    user_feedback TEXT,
    system_feedback TEXT,
    improvement_suggestions JSONB DEFAULT '[]',

    -- Learning Extraction
    learnings JSONB DEFAULT '[]',  -- Key learnings from this execution
    context_used JSONB,  -- What context was provided
    context_quality INTEGER CHECK (context_quality BETWEEN 1 AND 10),

    -- RLS
    CONSTRAINT feedback_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE agent_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_feedback_access"
ON agent_feedback
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_feedback_agent ON agent_feedback(agent_id);
CREATE INDEX idx_feedback_type ON agent_feedback(agent_type);
CREATE INDEX idx_feedback_date ON agent_feedback(execution_date DESC);
CREATE INDEX idx_feedback_status ON agent_feedback(status);
CREATE INDEX idx_feedback_quality ON agent_feedback(quality_rating DESC);
```

**Usage:**
- Track all agent executions across Department 3 (Execution Agents)
- Capture quality ratings and user feedback
- Enable Department 4 (System Evolution) continuous improvement
- Power agent factory optimization decisions
- Generate weekly improvement insights

**Sample Queries:**

```sql
-- Agent performance by type
SELECT
    agent_type,
    AVG(quality_rating) as avg_quality,
    AVG(execution_duration_seconds) as avg_duration,
    COUNT(*) as execution_count,
    COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*) as success_rate
FROM agent_feedback
WHERE execution_date > NOW() - INTERVAL '30 days'
GROUP BY agent_type
ORDER BY avg_quality DESC;

-- Top performing agents
SELECT
    agent_id,
    agent_type,
    AVG(quality_rating) as avg_quality,
    COUNT(*) as executions
FROM agent_feedback
WHERE execution_date > NOW() - INTERVAL '90 days'
GROUP BY agent_id, agent_type
HAVING COUNT(*) >= 5
ORDER BY avg_quality DESC
LIMIT 10;

-- Recent low-quality executions needing review
SELECT
    agent_id,
    task_description,
    quality_rating,
    user_feedback,
    improvement_suggestions
FROM agent_feedback
WHERE quality_rating < 5
  AND execution_date > NOW() - INTERVAL '7 days'
ORDER BY execution_date DESC;
```

**Related Documentation:** [SYSTEM_SPEC.md](../SYSTEM_SPEC.md) - See Pillar 5: GROW (System Evolution)

## Sample Queries for New Tables

### Energy Pattern Analysis

```sql
-- Daily energy summary
SELECT
    DATE(timestamp) as date,
    AVG(energy_level) as avg_energy,
    MODE() WITHIN GROUP (ORDER BY focus_quality) as primary_focus,
    COUNT(*) as measurement_count
FROM energy_tracking
WHERE user_id = 'gwasmuth@gmail.com'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Energy by time of day
SELECT
    EXTRACT(HOUR FROM timestamp) as hour,
    AVG(energy_level) as avg_energy,
    COUNT(*) as measurements
FROM energy_tracking
WHERE user_id = 'gwasmuth@gmail.com'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY hour
ORDER BY hour;
```

### OKR Progress Tracking

```sql
-- Current quarter OKR summary
SELECT
    objective_number,
    objective,
    key_result_number,
    key_result,
    current_value,
    target_value,
    progress_percentage,
    status
FROM okr_tracking
WHERE quarter = 'Q1 2026'
  AND tenant_id = 'default'
ORDER BY objective_number, key_result_number;

-- Weekly velocity calculation
WITH weekly_measurements AS (
    SELECT
        okr_id,
        DATE_TRUNC('week', measured_at) as week,
        AVG(measured_value) as avg_value
    FROM okr_measurements
    WHERE measured_at > NOW() - INTERVAL '4 weeks'
    GROUP BY okr_id, DATE_TRUNC('week', measured_at)
)
SELECT
    okr_id,
    week,
    avg_value,
    avg_value - LAG(avg_value) OVER (PARTITION BY okr_id ORDER BY week) as weekly_change
FROM weekly_measurements
ORDER BY okr_id, week DESC;
```

## Related Documentation

- [Vector Store Details](./VECTOR_STORE.md)
- [Knowledge Stores Overview](../knowledge-stores/OVERVIEW.md)
- [Knowledge Ingestion Service](../services/KNOWLEDGE_INGESTION.md)
- [OKR System](../services/OKR_SYSTEM.md)
- [Energy Tracking](../services/ENERGY_TRACKING.md)
- [System Specification](../SYSTEM_SPEC.md) - Canonical system reference

---

*See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for full documentation index.*
