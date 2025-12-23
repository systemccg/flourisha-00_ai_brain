-- ============================================================================
-- Flourisha AI Brain - Energy Tracking Migration
-- Purpose: Track energy levels and focus quality every 90 minutes
-- Multi-Tenant with Row-Level Security (RLS)
-- ============================================================================

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: Create energy_tracking table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.energy_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,  -- User who tracked this energy reading

    -- Energy tracking data
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    energy_level INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    focus_quality TEXT NOT NULL CHECK (focus_quality IN ('deep', 'shallow', 'distracted')),

    -- Tracking source
    source TEXT NOT NULL CHECK (source IN ('chrome_extension', 'sms', 'manual')),

    -- Optional contextual notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 2: Create indexes for optimal query performance
-- ---------------------------------------------------------------------------
-- Primary query pattern: Get energy tracking by tenant and time range
CREATE INDEX idx_energy_tenant_time
ON public.energy_tracking(tenant_id, timestamp DESC);

-- Query pattern: Get energy tracking by user and time range
CREATE INDEX idx_energy_user_time
ON public.energy_tracking(user_id, timestamp DESC);

-- Query pattern: Filter by focus quality for pattern analysis
CREATE INDEX idx_energy_focus_quality
ON public.energy_tracking(tenant_id, focus_quality, timestamp DESC);

-- Query pattern: Filter by energy level for pattern detection
CREATE INDEX idx_energy_level
ON public.energy_tracking(tenant_id, energy_level, timestamp DESC);

-- Step 3: Add table comments for documentation
-- ---------------------------------------------------------------------------
COMMENT ON TABLE public.energy_tracking IS 'Tracks user energy levels (1-10) and focus quality every 90 minutes for productivity analysis';
COMMENT ON COLUMN public.energy_tracking.energy_level IS 'Subjective energy level from 1 (exhausted) to 10 (peak energy)';
COMMENT ON COLUMN public.energy_tracking.focus_quality IS 'Quality of focus: deep (flow state), shallow (multitasking), distracted (interrupted)';
COMMENT ON COLUMN public.energy_tracking.source IS 'How the tracking was recorded: chrome_extension, sms, or manual entry';
COMMENT ON COLUMN public.energy_tracking.notes IS 'Optional contextual notes about environment, tasks, or circumstances';

-- Step 4: Enable Row Level Security (RLS)
-- ---------------------------------------------------------------------------
ALTER TABLE public.energy_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view energy tracking data for their tenant
CREATE POLICY "energy_tracking_tenant_isolation"
ON public.energy_tracking
FOR SELECT
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

-- RLS Policy: Users can only insert energy tracking for their tenant
CREATE POLICY "energy_tracking_insert_own_tenant"
ON public.energy_tracking
FOR INSERT
WITH CHECK (
    tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
    AND user_id = current_setting('request.jwt.claims', true)::json->>'sub'
);

-- RLS Policy: Users can only update their own energy tracking entries
CREATE POLICY "energy_tracking_update_own"
ON public.energy_tracking
FOR UPDATE
USING (
    tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id'
    AND user_id = current_setting('request.jwt.claims', true)::json->>'sub'
);

-- Step 5: Create function for automatic analytics
-- ---------------------------------------------------------------------------
-- Function to get average energy for a time range
CREATE OR REPLACE FUNCTION get_average_energy_for_period(
    p_tenant_id TEXT,
    p_user_id TEXT,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ
)
RETURNS TABLE (
    avg_energy NUMERIC,
    deep_focus_count BIGINT,
    shallow_focus_count BIGINT,
    distracted_count BIGINT,
    total_readings BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ROUND(AVG(energy_level)::NUMERIC, 2) as avg_energy,
        COUNT(*) FILTER (WHERE focus_quality = 'deep') as deep_focus_count,
        COUNT(*) FILTER (WHERE focus_quality = 'shallow') as shallow_focus_count,
        COUNT(*) FILTER (WHERE focus_quality = 'distracted') as distracted_count,
        COUNT(*) as total_readings
    FROM public.energy_tracking
    WHERE tenant_id = p_tenant_id
        AND user_id = p_user_id
        AND timestamp BETWEEN p_start_time AND p_end_time;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_average_energy_for_period IS 'Calculate average energy and focus quality distribution for a time period';

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert sample energy tracking entries for testing
-- Using cocreators_group tenant (assuming it exists from base schema)
INSERT INTO public.energy_tracking (tenant_id, user_id, timestamp, energy_level, focus_quality, source, notes)
VALUES
    (
        'cocreators_group',
        'kai_user_id',
        NOW() - INTERVAL '4 hours',
        8,
        'deep',
        'manual',
        'Morning session - high energy, working on database migrations'
    ),
    (
        'cocreators_group',
        'kai_user_id',
        NOW() - INTERVAL '2 hours 30 minutes',
        7,
        'deep',
        'chrome_extension',
        'Still focused, implementing TypeScript hooks'
    ),
    (
        'cocreators_group',
        'kai_user_id',
        NOW() - INTERVAL '1 hour',
        5,
        'shallow',
        'chrome_extension',
        'Post-lunch dip, doing code review'
    ),
    (
        'cocreators_group',
        'kai_user_id',
        NOW(),
        6,
        'distracted',
        'manual',
        'Multiple interruptions from Slack messages'
    )
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Completion Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Energy tracking schema created successfully!';
    RAISE NOTICE 'Table created: energy_tracking';
    RAISE NOTICE 'Indexes created: tenant_time, user_time, focus_quality, energy_level';
    RAISE NOTICE 'RLS policies enabled for multi-tenant security';
    RAISE NOTICE 'Helper function: get_average_energy_for_period()';
    RAISE NOTICE '';
    RAISE NOTICE 'Usage example:';
    RAISE NOTICE '  SELECT * FROM get_average_energy_for_period(';
    RAISE NOTICE '    ''cocreators_group'',';
    RAISE NOTICE '    ''kai_user_id'',';
    RAISE NOTICE '    NOW() - INTERVAL ''1 day'',';
    RAISE NOTICE '    NOW()';
    RAISE NOTICE '  );';
END $$;
