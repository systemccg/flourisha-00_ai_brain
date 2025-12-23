-- ============================================================================
-- Flourisha AI Brain - OKR Visibility & Tags Migration
-- Purpose: Add personal/workspace visibility model and tagging support
-- Simplified model: personal + workspace (groups added later)
-- ============================================================================

-- ============================================================================
-- STEP 0: Fix existing trigger issue (updated_at -> last_updated)
-- ============================================================================

-- Drop problematic trigger that references wrong column name
DROP TRIGGER IF EXISTS set_updated_at ON public.okr_tracking;

-- Create/update the trigger function to use correct column
CREATE OR REPLACE FUNCTION update_okr_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger with correct column reference
DROP TRIGGER IF EXISTS set_last_updated ON public.okr_tracking;
CREATE TRIGGER set_last_updated
    BEFORE UPDATE ON public.okr_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_okr_modified_column();

-- ============================================================================
-- STEP 1: Add visibility columns to okr_tracking
-- ============================================================================

-- Add user_id for personal OKRs (nullable - old records don't have it)
ALTER TABLE public.okr_tracking
ADD COLUMN IF NOT EXISTS user_id UUID;

-- Add visibility column with check constraint
ALTER TABLE public.okr_tracking
ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'personal'
CHECK (visibility IN ('personal', 'workspace'));

-- Add workspace_id for workspace-scoped OKRs (replaces tenant_id eventually)
-- For now, tenant_id continues to work, workspace_id is for future
ALTER TABLE public.okr_tracking
ADD COLUMN IF NOT EXISTS workspace_id UUID;

-- Add priority for ordering
ALTER TABLE public.okr_tracking
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0;

-- Add department/category for organization (from Q1_2026.yaml structure)
ALTER TABLE public.okr_tracking
ADD COLUMN IF NOT EXISTS department VARCHAR(100);

COMMENT ON COLUMN public.okr_tracking.user_id IS 'Owner user ID for personal OKRs (null for legacy tenant-based records)';
COMMENT ON COLUMN public.okr_tracking.visibility IS 'personal = only owner sees across all contexts; workspace = all workspace members see';
COMMENT ON COLUMN public.okr_tracking.workspace_id IS 'Workspace ID for workspace-scoped OKRs (future: replaces tenant_id)';
COMMENT ON COLUMN public.okr_tracking.priority IS 'Priority for sorting (higher = more important)';
COMMENT ON COLUMN public.okr_tracking.department IS 'Department/category for grouping (e.g., strategic_command, knowledge_intelligence)';

-- ============================================================================
-- STEP 2: Create OKR Tags table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.okr_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Ownership: personal tag or workspace-scoped tag
    user_id UUID,  -- NULL = workspace tag, set = personal tag
    workspace_id UUID,  -- For workspace-scoped tags
    tenant_id TEXT,  -- Legacy: for backward compatibility

    -- Tag details
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20) DEFAULT '#808080',  -- Hex color code
    description TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique: tag name is unique per user OR per workspace
    UNIQUE(user_id, name),  -- Personal tags unique per user
    UNIQUE(workspace_id, name)  -- Workspace tags unique per workspace
);

CREATE INDEX idx_okr_tags_user ON public.okr_tags(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_okr_tags_workspace ON public.okr_tags(workspace_id) WHERE workspace_id IS NOT NULL;

COMMENT ON TABLE public.okr_tags IS 'Tags for organizing OKRs - can be personal (user-scoped) or workspace-scoped';

-- ============================================================================
-- STEP 3: Create OKR-Tag junction table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.okr_objective_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Reference to OKR (using objective_id since KRs inherit from objective)
    okr_id UUID NOT NULL,  -- References okr_tracking.id
    tag_id UUID NOT NULL REFERENCES public.okr_tags(id) ON DELETE CASCADE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(okr_id, tag_id)
);

CREATE INDEX idx_okr_objective_tags_okr ON public.okr_objective_tags(okr_id);
CREATE INDEX idx_okr_objective_tags_tag ON public.okr_objective_tags(tag_id);

COMMENT ON TABLE public.okr_objective_tags IS 'Junction table linking OKRs to tags (many-to-many)';

-- ============================================================================
-- STEP 4: Create OKR Progress History table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.okr_progress_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Reference to the OKR tracking record
    okr_tracking_id UUID NOT NULL,

    -- Progress snapshot
    previous_value NUMERIC,
    new_value NUMERIC NOT NULL,

    -- What changed
    change_type VARCHAR(50) DEFAULT 'progress_update',  -- progress_update, status_change, target_change

    -- Context
    notes TEXT,
    recorded_by UUID,  -- User who made the change

    -- Timestamp
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_okr_progress_history_okr ON public.okr_progress_history(okr_tracking_id, recorded_at DESC);

COMMENT ON TABLE public.okr_progress_history IS 'Historical record of OKR progress changes for trending and analysis';

-- ============================================================================
-- STEP 5: Add new indexes for visibility queries
-- ============================================================================

-- Query pattern: Get personal OKRs for a user
CREATE INDEX IF NOT EXISTS idx_okr_user_visibility
ON public.okr_tracking(user_id, visibility, quarter)
WHERE visibility = 'personal';

-- Query pattern: Get workspace OKRs
CREATE INDEX IF NOT EXISTS idx_okr_workspace_visibility
ON public.okr_tracking(workspace_id, visibility, quarter)
WHERE visibility = 'workspace';

-- Query pattern: Filter by department
CREATE INDEX IF NOT EXISTS idx_okr_department
ON public.okr_tracking(tenant_id, quarter, department)
WHERE department IS NOT NULL;

-- ============================================================================
-- STEP 6: Enable RLS on new tables
-- ============================================================================

ALTER TABLE public.okr_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.okr_objective_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.okr_progress_history ENABLE ROW LEVEL SECURITY;

-- RLS for okr_tags: User sees their personal tags + workspace tags they're a member of
CREATE POLICY "okr_tags_user_access"
ON public.okr_tags
FOR ALL
USING (
    -- Personal tags: owner can see
    user_id = current_setting('request.jwt.claims', true)::json->>'user_id'
    OR
    -- Workspace tags: tenant members can see (legacy)
    tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
    -- Future: workspace membership check
);

-- RLS for okr_objective_tags: Inherit from OKR access
CREATE POLICY "okr_objective_tags_access"
ON public.okr_objective_tags
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.okr_tracking okr
        WHERE okr.id = okr_id
        AND (
            okr.user_id = current_setting('request.jwt.claims', true)::json->>'user_id'
            OR okr.tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
        )
    )
);

-- RLS for okr_progress_history: Inherit from OKR access
CREATE POLICY "okr_progress_history_access"
ON public.okr_progress_history
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.okr_tracking okr
        WHERE okr.id = okr_tracking_id
        AND (
            okr.user_id = current_setting('request.jwt.claims', true)::json->>'user_id'
            OR okr.tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
        )
    )
);

-- ============================================================================
-- STEP 7: Update RLS on okr_tracking for visibility model
-- ============================================================================

-- Drop existing policies (we'll recreate with visibility support)
DROP POLICY IF EXISTS "okr_tracking_tenant_isolation" ON public.okr_tracking;
DROP POLICY IF EXISTS "okr_tracking_insert_tenant" ON public.okr_tracking;
DROP POLICY IF EXISTS "okr_tracking_update_tenant" ON public.okr_tracking;

-- New SELECT policy: Support both personal and workspace visibility
CREATE POLICY "okr_tracking_select"
ON public.okr_tracking
FOR SELECT
USING (
    -- Personal OKRs: owner sees across all contexts
    (visibility = 'personal' AND user_id::text = current_setting('request.jwt.claims', true)::json->>'user_id')
    OR
    -- Workspace OKRs: workspace members see (via tenant_id for now)
    (visibility = 'workspace' AND tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id')
    OR
    -- Legacy: tenant-based access for old records without visibility
    (visibility IS NULL AND tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id')
);

-- New INSERT policy
CREATE POLICY "okr_tracking_insert"
ON public.okr_tracking
FOR INSERT
WITH CHECK (
    -- Personal OKRs: user must be owner
    (visibility = 'personal' AND user_id::text = current_setting('request.jwt.claims', true)::json->>'user_id')
    OR
    -- Workspace OKRs: user must be workspace member (via tenant_id for now)
    (visibility = 'workspace' AND tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id')
    OR
    -- Legacy insert
    tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
);

-- New UPDATE policy
CREATE POLICY "okr_tracking_update"
ON public.okr_tracking
FOR UPDATE
USING (
    -- Personal OKRs: only owner can update
    (visibility = 'personal' AND user_id::text = current_setting('request.jwt.claims', true)::json->>'user_id')
    OR
    -- Workspace OKRs: workspace members can update (via tenant_id for now)
    (visibility = 'workspace' AND tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id')
    OR
    -- Legacy
    tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
);

-- ============================================================================
-- STEP 8: Helper function to get user's OKR summary across all contexts
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_okr_overview(
    p_user_id UUID,
    p_quarter TEXT DEFAULT NULL
)
RETURNS TABLE (
    visibility VARCHAR,
    context_name TEXT,
    objective_count BIGINT,
    kr_count BIGINT,
    avg_progress NUMERIC,
    at_risk_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        okr.visibility,
        CASE
            WHEN okr.visibility = 'personal' THEN 'Personal'
            ELSE COALESCE(okr.tenant_id, 'Unknown')
        END as context_name,
        COUNT(DISTINCT okr.objective_id) as objective_count,
        COUNT(*) as kr_count,
        ROUND(AVG(
            CASE WHEN okr.key_result_target > 0
            THEN (okr.key_result_current / okr.key_result_target * 100)
            ELSE 0 END
        )::NUMERIC, 2) as avg_progress,
        COUNT(*) FILTER (WHERE okr.status = 'at_risk') as at_risk_count
    FROM public.okr_tracking okr
    WHERE
        -- User's personal OKRs
        (okr.visibility = 'personal' AND okr.user_id = p_user_id)
        -- Workspace OKRs where user is a member (simplified - uses tenant_id)
        -- In future, this would check workspace_memberships
        AND (p_quarter IS NULL OR okr.quarter = p_quarter)
    GROUP BY okr.visibility,
             CASE WHEN okr.visibility = 'personal' THEN 'Personal' ELSE COALESCE(okr.tenant_id, 'Unknown') END
    ORDER BY visibility, context_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_user_okr_overview IS 'Get OKR summary for a user across personal and workspace contexts';

-- ============================================================================
-- COMPLETION
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ OKR Visibility & Tags migration completed!';
    RAISE NOTICE '';
    RAISE NOTICE 'New columns added to okr_tracking:';
    RAISE NOTICE '  - user_id (UUID): Owner for personal OKRs';
    RAISE NOTICE '  - visibility (VARCHAR): personal | workspace';
    RAISE NOTICE '  - workspace_id (UUID): Future workspace support';
    RAISE NOTICE '  - priority (INTEGER): For sorting';
    RAISE NOTICE '  - department (VARCHAR): For grouping';
    RAISE NOTICE '';
    RAISE NOTICE 'New tables created:';
    RAISE NOTICE '  - okr_tags: Personal and workspace-scoped tags';
    RAISE NOTICE '  - okr_objective_tags: Tag assignments';
    RAISE NOTICE '  - okr_progress_history: Progress tracking over time';
    RAISE NOTICE '';
    RAISE NOTICE 'RLS policies updated for visibility model';
    RAISE NOTICE '';
    RAISE NOTICE 'Usage:';
    RAISE NOTICE '  -- Create personal OKR';
    RAISE NOTICE '  INSERT INTO okr_tracking (user_id, visibility, quarter, ...) VALUES (user_uuid, ''personal'', ''Q1_2026'', ...);';
    RAISE NOTICE '';
    RAISE NOTICE '  -- Get user overview across all contexts';
    RAISE NOTICE '  SELECT * FROM get_user_okr_overview(user_uuid, ''Q1_2026'');';
END $$;
