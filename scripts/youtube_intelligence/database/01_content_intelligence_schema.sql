-- ============================================================================
-- Flourisha Content Intelligence Database Schema
-- Multi-Tenant with Row-Level Security (RLS) and RBAC
-- ============================================================================

-- Step 1: Add groups column to existing tenant_users table
-- ---------------------------------------------------------------------------
ALTER TABLE public.tenant_users
ADD COLUMN IF NOT EXISTS groups JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN public.tenant_users.groups IS 'Array of group names user belongs to, e.g. ["engineering", "product_development"]';

CREATE INDEX IF NOT EXISTS idx_tenant_users_groups ON public.tenant_users USING gin(groups);


-- Step 2: Projects table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- YouTube integration
    youtube_playlist_id VARCHAR(255),

    -- Project configuration
    tech_stack JSONB DEFAULT '{}'::jsonb,
    context_config JSONB DEFAULT '{}'::jsonb,

    -- Default visibility rules per tag/category
    visibility_defaults JSONB DEFAULT jsonb_build_object(
        'default', 'private',
        'tag_rules', jsonb_build_object(
            'personal-learning', 'private',
            'flourisha-enhancement', 'group:engineering',
            'company-announcement', 'tenant'
        )
    ),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_user_id TEXT,

    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_projects_tenant ON public.projects(tenant_id);
CREATE INDEX idx_projects_playlist ON public.projects(youtube_playlist_id) WHERE youtube_playlist_id IS NOT NULL;

COMMENT ON TABLE public.projects IS 'Projects for organizing content by category/purpose';
COMMENT ON COLUMN public.projects.visibility_defaults IS 'Default visibility rules for content added to this project';


-- Step 3: Input sources table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.input_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    tenant_user_id TEXT NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,

    -- Source configuration
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('youtube', 'limitless', 'meeting', 'manual', 'voice_note')),
    source_identifier VARCHAR(500),  -- playlist_id, channel_id, limitless_tag, etc.
    config JSONB DEFAULT '{}'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_input_sources_tenant ON public.input_sources(tenant_id);
CREATE INDEX idx_input_sources_project ON public.input_sources(project_id);
CREATE INDEX idx_input_sources_type ON public.input_sources(source_type, is_active) WHERE is_active = TRUE;

COMMENT ON TABLE public.input_sources IS 'Input sources (YouTube playlists, Limitless tags, etc.) for automatic content processing';


-- Step 4: Processed content table (main content storage)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.processed_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL,
    tenant_user_id TEXT NOT NULL,
    created_by_user_id TEXT NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,

    -- Access control (RBAC)
    visibility VARCHAR(50) DEFAULT 'private' CHECK (visibility IN ('private', 'tenant') OR visibility LIKE 'group:%'),
    shared_with JSONB DEFAULT '[]'::jsonb,  -- Array of 'group:X' or 'user:Y'

    -- Content metadata
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(500),  -- video_id, note_id, etc.
    title VARCHAR(1000),
    content_url TEXT,

    -- Processed content
    raw_content TEXT,
    transcript TEXT,
    summary TEXT,
    key_insights JSONB DEFAULT '[]'::jsonb,
    action_items JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    categories JSONB DEFAULT '[]'::jsonb,
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0 AND relevance_score <= 10),

    -- Storage locations
    file_path TEXT,  -- Path to markdown file
    vector_id TEXT,  -- ID in vector database
    graph_node_id TEXT,  -- ID in Neo4j

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_content_tenant_user ON public.processed_content(tenant_id, tenant_user_id);
CREATE INDEX idx_content_project ON public.processed_content(project_id);
CREATE INDEX idx_content_visibility ON public.processed_content(tenant_id, visibility);
CREATE INDEX idx_content_shared ON public.processed_content USING gin(shared_with);
CREATE INDEX idx_content_status ON public.processed_content(processing_status, created_at) WHERE processing_status != 'completed';
CREATE INDEX idx_content_tags ON public.processed_content USING gin(tags);
CREATE INDEX idx_content_relevance ON public.processed_content(project_id, relevance_score DESC);

COMMENT ON TABLE public.processed_content IS 'Main table for all processed content with multi-tenant RBAC';
COMMENT ON COLUMN public.processed_content.visibility IS 'Who can see this: private, tenant, or group:groupname';
COMMENT ON COLUMN public.processed_content.shared_with IS 'Array of groups or users, e.g. ["group:engineering", "user:joanna"]';


-- Step 5: YouTube subscriptions table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.youtube_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    tenant_user_id TEXT NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,

    -- YouTube channel/playlist info
    channel_id VARCHAR(255),
    channel_name VARCHAR(500),
    playlist_id VARCHAR(255),  -- If subscribing to specific playlist

    -- Subscription settings
    alerts_enabled BOOLEAN DEFAULT TRUE,
    auto_process BOOLEAN DEFAULT TRUE,

    -- Status
    last_checked TIMESTAMP WITH TIME ZONE,
    last_video_processed VARCHAR(255),  -- Last video_id processed

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(tenant_id, channel_id, playlist_id)
);

CREATE INDEX idx_youtube_subs_tenant ON public.youtube_subscriptions(tenant_id);
CREATE INDEX idx_youtube_subs_project ON public.youtube_subscriptions(project_id);
CREATE INDEX idx_youtube_subs_active ON public.youtube_subscriptions(alerts_enabled, auto_process) WHERE alerts_enabled = TRUE AND auto_process = TRUE;

COMMENT ON TABLE public.youtube_subscriptions IS 'YouTube channel/playlist subscriptions for automatic content processing';


-- Step 6: Processing queue table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.processing_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    content_id UUID REFERENCES public.processed_content(id) ON DELETE CASCADE,

    -- Queue management
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Status
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_queue_status_priority ON public.processing_queue(status, priority DESC, created_at) WHERE status = 'queued';
CREATE INDEX idx_queue_tenant ON public.processing_queue(tenant_id);
CREATE INDEX idx_queue_retry ON public.processing_queue(next_retry_at) WHERE status = 'failed' AND retry_count < max_retries;

COMMENT ON TABLE public.processing_queue IS 'Queue for async content processing with retry logic';


-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.input_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processed_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.youtube_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_queue ENABLE ROW LEVEL SECURITY;


-- Projects RLS: Users can only see projects in their tenant
CREATE POLICY "projects_tenant_isolation"
ON public.projects
FOR ALL
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');


-- Input sources RLS: Users can only see input sources in their tenant
CREATE POLICY "input_sources_tenant_isolation"
ON public.input_sources
FOR ALL
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');


-- Processed content RLS: Complex visibility rules
CREATE POLICY "content_visibility_control"
ON public.processed_content
FOR SELECT
USING (
    -- User owns the content
    created_by_user_id = (current_setting('request.jwt.claims', true)::json->>'sub')
    OR
    -- Content is tenant-wide and same tenant
    (
        visibility = 'tenant'
        AND tenant_id = (current_setting('request.jwt.claims', true)::json->>'tenant_id')
    )
    OR
    -- User is in a shared group
    EXISTS (
        SELECT 1
        FROM public.tenant_users tu
        WHERE tu.user_id = (current_setting('request.jwt.claims', true)::json->>'sub')
        AND tu.tenant_id = processed_content.tenant_id
        AND tu.groups ?| (
            SELECT array_agg(jsonb_array_elements_text(shared_with))
            FROM (SELECT shared_with) s
        )
    )
    OR
    -- Content explicitly shared with this user
    shared_with @> jsonb_build_array('user:' || (current_setting('request.jwt.claims', true)::json->>'sub'))
);

-- Content insert/update: Users can only modify their own content
CREATE POLICY "content_modify_own"
ON public.processed_content
FOR INSERT
WITH CHECK (
    tenant_id = (current_setting('request.jwt.claims', true)::json->>'tenant_id')
    AND tenant_user_id = (current_setting('request.jwt.claims', true)::json->>'sub')
);

CREATE POLICY "content_update_own"
ON public.processed_content
FOR UPDATE
USING (created_by_user_id = (current_setting('request.jwt.claims', true)::json->>'sub'));


-- YouTube subscriptions RLS: Users can only see subscriptions in their tenant
CREATE POLICY "youtube_subs_tenant_isolation"
ON public.youtube_subscriptions
FOR ALL
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');


-- Processing queue RLS: Service role only (backend processing)
CREATE POLICY "queue_service_role"
ON public.processing_queue
FOR ALL
USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');


-- ============================================================================
-- Functions & Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all tables
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_input_sources_updated_at BEFORE UPDATE ON public.input_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processed_content_updated_at BEFORE UPDATE ON public.processed_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_youtube_subs_updated_at BEFORE UPDATE ON public.youtube_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert sample tenant (if doesn't exist)
INSERT INTO public.tenants (tenant_id, name, slug, description, subscription_tier)
VALUES ('cocreators_group', 'CoCreators Group', 'cocreators', 'Flourisha development and operations', 'enterprise')
ON CONFLICT (tenant_id) DO NOTHING;

-- Insert sample project
INSERT INTO public.projects (tenant_id, name, description, youtube_playlist_id, tech_stack, visibility_defaults)
VALUES (
    'cocreators_group',
    'flourisha-enhancements',
    'Infrastructure improvements and automation for Flourisha AI',
    NULL,  -- Will be filled in later
    '{"database": "Supabase", "backend": "FastAPI + Pydantic AI", "frontend": "React/Next.js", "graph_db": "Neo4j", "vector_db": "PG Vector"}'::jsonb,
    '{"default": "group:engineering", "tag_rules": {"personal-learning": "private", "flourisha-enhancement": "group:engineering", "company-announcement": "tenant"}}'::jsonb
)
ON CONFLICT (tenant_id, name) DO UPDATE
SET
    tech_stack = EXCLUDED.tech_stack,
    visibility_defaults = EXCLUDED.visibility_defaults;


-- ============================================================================
-- Completion Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Content Intelligence schema created successfully!';
    RAISE NOTICE 'Tables created: projects, input_sources, processed_content, youtube_subscriptions, processing_queue';
    RAISE NOTICE 'RLS policies enabled for multi-tenant security';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Configure Firebase Auth';
    RAISE NOTICE '2. Set up JWT validation in Supabase';
    RAISE NOTICE '3. Test authentication flow';
END $$;
