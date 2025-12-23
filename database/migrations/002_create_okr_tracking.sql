-- ============================================================================
-- Flourisha AI Brain - OKR Tracking Migration
-- Purpose: Track quarterly Objectives and Key Results (OKRs) with progress
-- Multi-Tenant with Row-Level Security (RLS)
-- ============================================================================

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: Create okr_tracking table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.okr_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,

    -- Quarter and objective hierarchy
    quarter TEXT NOT NULL,  -- e.g., 'Q1_2026', 'Q2_2025'
    objective_id TEXT NOT NULL,  -- Unique within tenant+quarter, e.g., 'OBJ-001'
    objective_title TEXT NOT NULL,
    objective_description TEXT,
    owner TEXT,  -- Owner user_id or team name
    target_completion_date DATE,

    -- Key result details
    key_result_id TEXT NOT NULL,  -- Unique within objective, e.g., 'KR-001', 'KR-002'
    key_result_title TEXT NOT NULL,
    key_result_target NUMERIC NOT NULL,  -- Target value to achieve
    key_result_current NUMERIC DEFAULT 0,  -- Current progress value
    key_result_unit TEXT,  -- e.g., '%', 'count', 'hours', 'users', 'revenue'

    -- Status tracking
    status TEXT DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'at_risk', 'paused')),

    -- Timestamps
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique combination of tenant + quarter + objective + key_result
    UNIQUE(tenant_id, quarter, objective_id, key_result_id)
);

-- Step 2: Create indexes for optimal query performance
-- ---------------------------------------------------------------------------
-- Primary query pattern: Get all OKRs for a tenant and quarter
CREATE INDEX idx_okr_tenant_quarter
ON public.okr_tracking(tenant_id, quarter, objective_id);

-- Query pattern: Filter by status for at-risk or in-progress tracking
CREATE INDEX idx_okr_status
ON public.okr_tracking(status, tenant_id, quarter)
WHERE status IN ('in_progress', 'at_risk');

-- Query pattern: Get OKRs by owner for individual/team tracking
CREATE INDEX idx_okr_owner
ON public.okr_tracking(tenant_id, owner, quarter);

-- Query pattern: Get OKRs by target date for deadline tracking
CREATE INDEX idx_okr_target_date
ON public.okr_tracking(tenant_id, target_completion_date)
WHERE target_completion_date IS NOT NULL;

-- Step 3: Add table comments for documentation
-- ---------------------------------------------------------------------------
COMMENT ON TABLE public.okr_tracking IS 'Tracks quarterly Objectives and Key Results (OKRs) with progress and status monitoring';
COMMENT ON COLUMN public.okr_tracking.quarter IS 'Quarter identifier in format Q#_YYYY (e.g., Q1_2026, Q4_2025)';
COMMENT ON COLUMN public.okr_tracking.objective_id IS 'Unique objective identifier within tenant+quarter scope';
COMMENT ON COLUMN public.okr_tracking.key_result_id IS 'Unique key result identifier within objective scope';
COMMENT ON COLUMN public.okr_tracking.key_result_target IS 'Target value to achieve for this key result';
COMMENT ON COLUMN public.okr_tracking.key_result_current IS 'Current progress value (updated as work progresses)';
COMMENT ON COLUMN public.okr_tracking.key_result_unit IS 'Unit of measurement: %, count, hours, users, revenue, etc.';
COMMENT ON COLUMN public.okr_tracking.status IS 'Current status: not_started, in_progress, completed, at_risk, or paused';

-- Step 4: Enable Row Level Security (RLS)
-- ---------------------------------------------------------------------------
ALTER TABLE public.okr_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view OKRs for their tenant
CREATE POLICY "okr_tracking_tenant_isolation"
ON public.okr_tracking
FOR SELECT
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

-- RLS Policy: Users can insert OKRs for their tenant
CREATE POLICY "okr_tracking_insert_tenant"
ON public.okr_tracking
FOR INSERT
WITH CHECK (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

-- RLS Policy: Users can update OKRs in their tenant
CREATE POLICY "okr_tracking_update_tenant"
ON public.okr_tracking
FOR UPDATE
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

-- Step 5: Create trigger to auto-update last_updated timestamp
-- ---------------------------------------------------------------------------
CREATE TRIGGER update_okr_tracking_timestamp
BEFORE UPDATE ON public.okr_tracking
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Note: update_updated_at_column() function already exists from base schema
-- It updates the last_updated timestamp automatically on any row update

-- Step 6: Create helper functions for OKR analytics
-- ---------------------------------------------------------------------------
-- Function to calculate OKR completion percentage
CREATE OR REPLACE FUNCTION calculate_okr_progress(
    p_tenant_id TEXT,
    p_quarter TEXT,
    p_objective_id TEXT
)
RETURNS TABLE (
    objective_id TEXT,
    objective_title TEXT,
    total_key_results BIGINT,
    completed_key_results BIGINT,
    overall_progress_pct NUMERIC,
    status_summary JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        okr.objective_id,
        MAX(okr.objective_title) as objective_title,
        COUNT(*) as total_key_results,
        COUNT(*) FILTER (WHERE okr.status = 'completed') as completed_key_results,
        ROUND(
            AVG(
                CASE
                    WHEN okr.key_result_target > 0
                    THEN LEAST(100, (okr.key_result_current / okr.key_result_target * 100))
                    ELSE 0
                END
            )::NUMERIC,
            2
        ) as overall_progress_pct,
        jsonb_object_agg(
            okr.status,
            COUNT(*)
        ) as status_summary
    FROM public.okr_tracking okr
    WHERE okr.tenant_id = p_tenant_id
        AND okr.quarter = p_quarter
        AND (p_objective_id IS NULL OR okr.objective_id = p_objective_id)
    GROUP BY okr.objective_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION calculate_okr_progress IS 'Calculate overall progress and status distribution for objectives';

-- Function to get at-risk OKRs (target date approaching with low progress)
CREATE OR REPLACE FUNCTION get_at_risk_okrs(
    p_tenant_id TEXT,
    p_quarter TEXT,
    p_days_threshold INTEGER DEFAULT 30
)
RETURNS TABLE (
    objective_id TEXT,
    objective_title TEXT,
    key_result_id TEXT,
    key_result_title TEXT,
    progress_pct NUMERIC,
    target_date DATE,
    days_remaining INTEGER,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        okr.objective_id,
        okr.objective_title,
        okr.key_result_id,
        okr.key_result_title,
        ROUND(
            CASE
                WHEN okr.key_result_target > 0
                THEN (okr.key_result_current / okr.key_result_target * 100)
                ELSE 0
            END::NUMERIC,
            2
        ) as progress_pct,
        okr.target_completion_date,
        (okr.target_completion_date - CURRENT_DATE) as days_remaining,
        okr.status
    FROM public.okr_tracking okr
    WHERE okr.tenant_id = p_tenant_id
        AND okr.quarter = p_quarter
        AND okr.target_completion_date IS NOT NULL
        AND okr.target_completion_date <= CURRENT_DATE + p_days_threshold
        AND okr.status NOT IN ('completed', 'paused')
        AND (
            CASE
                WHEN okr.key_result_target > 0
                THEN (okr.key_result_current / okr.key_result_target * 100)
                ELSE 0
            END
        ) < 70  -- Less than 70% complete
    ORDER BY okr.target_completion_date ASC, progress_pct ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_at_risk_okrs IS 'Identify OKRs at risk: approaching deadline with less than 70% progress';

-- ============================================================================
-- Sample Data (for testing - Q1 2026 Objectives)
-- ============================================================================

-- Objective 1: Launch Flourisha AI Brain Phase 1
INSERT INTO public.okr_tracking (tenant_id, quarter, objective_id, objective_title, objective_description, owner, target_completion_date, key_result_id, key_result_title, key_result_target, key_result_current, key_result_unit, status)
VALUES
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-001',
        'Launch Flourisha AI Brain Phase 1',
        'Deploy core AI brain infrastructure with energy tracking, OKR management, and evening analysis',
        'kai_user_id',
        '2026-03-31',
        'KR-001',
        'Complete database migrations for energy and OKR tracking',
        2,  -- 2 migrations total
        2,  -- Both completed
        'count',
        'completed'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-001',
        'Launch Flourisha AI Brain Phase 1',
        'Deploy core AI brain infrastructure with energy tracking, OKR management, and evening analysis',
        'kai_user_id',
        '2026-03-31',
        'KR-002',
        'Implement and test evening productivity analysis hook',
        1,  -- 1 hook to implement
        0,  -- In progress
        'count',
        'in_progress'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-001',
        'Launch Flourisha AI Brain Phase 1',
        'Deploy core AI brain infrastructure with energy tracking, OKR management, and evening analysis',
        'kai_user_id',
        '2026-03-31',
        'KR-003',
        'Achieve 80%+ code coverage with automated tests',
        80,  -- 80% target
        0,  -- Not started
        '%',
        'not_started'
    );

-- Objective 2: Optimize Developer Productivity Workflows
INSERT INTO public.okr_tracking (tenant_id, quarter, objective_id, objective_title, objective_description, owner, target_completion_date, key_result_id, key_result_title, key_result_target, key_result_current, key_result_unit, status)
VALUES
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-002',
        'Optimize Developer Productivity Workflows',
        'Streamline development processes with automation and better tooling',
        'engineering_team',
        '2026-03-31',
        'KR-001',
        'Reduce average PR review time to under 4 hours',
        4,  -- Target: 4 hours
        6,  -- Current: 6 hours
        'hours',
        'in_progress'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-002',
        'Optimize Developer Productivity Workflows',
        'Streamline development processes with automation and better tooling',
        'engineering_team',
        '2026-03-31',
        'KR-002',
        'Automate 90% of deployment pipeline',
        90,  -- Target: 90%
        60,  -- Current: 60%
        '%',
        'in_progress'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-002',
        'Optimize Developer Productivity Workflows',
        'Streamline development processes with automation and better tooling',
        'engineering_team',
        '2026-03-31',
        'KR-003',
        'Achieve 95%+ uptime for development services',
        95,  -- Target: 95%
        98,  -- Current: 98% (exceeding target!)
        '%',
        'completed'
    );

-- Objective 3: Improve Content Intelligence Processing
INSERT INTO public.okr_tracking (tenant_id, quarter, objective_id, objective_title, objective_description, owner, target_completion_date, key_result_id, key_result_title, key_result_target, key_result_current, key_result_unit, status)
VALUES
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-003',
        'Improve Content Intelligence Processing',
        'Enhance AI-powered content processing pipeline for better insights',
        'ai_team',
        '2026-03-31',
        'KR-001',
        'Process 1000+ content items with AI analysis',
        1000,  -- Target: 1000 items
        245,  -- Current: 245 items
        'count',
        'in_progress'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-003',
        'Improve Content Intelligence Processing',
        'Enhance AI-powered content processing pipeline for better insights',
        'ai_team',
        '2026-03-31',
        'KR-002',
        'Achieve 90%+ accuracy in content categorization',
        90,  -- Target: 90%
        85,  -- Current: 85%
        '%',
        'at_risk'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-003',
        'Improve Content Intelligence Processing',
        'Enhance AI-powered content processing pipeline for better insights',
        'ai_team',
        '2026-03-31',
        'KR-003',
        'Reduce average processing time to under 30 seconds',
        30,  -- Target: 30 seconds
        45,  -- Current: 45 seconds
        'seconds',
        'in_progress'
    );

-- Objective 4: Scale Multi-Tenant Infrastructure
INSERT INTO public.okr_tracking (tenant_id, quarter, objective_id, objective_title, objective_description, owner, target_completion_date, key_result_id, key_result_title, key_result_target, key_result_current, key_result_unit, status)
VALUES
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-004',
        'Scale Multi-Tenant Infrastructure',
        'Prepare infrastructure to support 100+ tenants with enterprise-grade performance',
        'infrastructure_team',
        '2026-03-31',
        'KR-001',
        'Support 100+ concurrent tenants',
        100,  -- Target: 100 tenants
        12,  -- Current: 12 tenants
        'count',
        'in_progress'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-004',
        'Scale Multi-Tenant Infrastructure',
        'Prepare infrastructure to support 100+ tenants with enterprise-grade performance',
        'infrastructure_team',
        '2026-03-31',
        'KR-002',
        'Maintain sub-100ms query response time at scale',
        100,  -- Target: 100ms
        75,  -- Current: 75ms
        'ms',
        'completed'
    ),
    (
        'cocreators_group',
        'Q1_2026',
        'OBJ-004',
        'Scale Multi-Tenant Infrastructure',
        'Prepare infrastructure to support 100+ tenants with enterprise-grade performance',
        'infrastructure_team',
        '2026-03-31',
        'KR-003',
        'Implement automated tenant provisioning',
        1,  -- Target: System implemented
        0,  -- Current: Not started
        'boolean',
        'not_started'
    );

-- ============================================================================
-- Completion Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ OKR tracking schema created successfully!';
    RAISE NOTICE 'Table created: okr_tracking';
    RAISE NOTICE 'Indexes created: tenant_quarter, status, owner, target_date';
    RAISE NOTICE 'RLS policies enabled for multi-tenant security';
    RAISE NOTICE 'Helper functions: calculate_okr_progress(), get_at_risk_okrs()';
    RAISE NOTICE '';
    RAISE NOTICE 'Sample data: 4 objectives with 13 key results for Q1 2026';
    RAISE NOTICE '';
    RAISE NOTICE 'Usage examples:';
    RAISE NOTICE '  -- Get progress for all objectives';
    RAISE NOTICE '  SELECT * FROM calculate_okr_progress(''cocreators_group'', ''Q1_2026'', NULL);';
    RAISE NOTICE '';
    RAISE NOTICE '  -- Get at-risk OKRs (within 30 days, <70% complete)';
    RAISE NOTICE '  SELECT * FROM get_at_risk_okrs(''cocreators_group'', ''Q1_2026'', 30);';
END $$;
