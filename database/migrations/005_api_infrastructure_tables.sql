-- ============================================================================
-- Flourisha AI Brain - API Infrastructure Tables Migration
-- Purpose: Create tables required for API infrastructure features
-- Multi-Tenant with Row-Level Security (RLS)
-- ============================================================================

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Step 1: Schema Migrations Tracking Table
-- ============================================================================
-- Tracks which migrations have been applied to the database
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    migration_id TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checksum TEXT,
    notes TEXT
);

COMMENT ON TABLE public.schema_migrations IS 'Tracks applied database migrations';
COMMENT ON COLUMN public.schema_migrations.migration_id IS 'Migration file identifier (filename without extension)';
COMMENT ON COLUMN public.schema_migrations.checksum IS 'MD5 checksum of migration file at time of application';

-- ============================================================================
-- Step 2: Cron Logs Table
-- ============================================================================
-- Tracks execution of scheduled cron jobs
CREATE TABLE IF NOT EXISTS public.cron_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Job identification
    job_type TEXT NOT NULL,

    -- Execution details
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'partial', 'skipped')),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER NOT NULL DEFAULT 0,

    -- Results
    message TEXT,
    error TEXT,
    details JSONB,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for cron_logs
CREATE INDEX IF NOT EXISTS idx_cron_logs_job_type ON public.cron_logs(job_type, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_cron_logs_status ON public.cron_logs(status, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_cron_logs_executed ON public.cron_logs(executed_at DESC);

COMMENT ON TABLE public.cron_logs IS 'Tracks scheduled job executions with status and duration';
COMMENT ON COLUMN public.cron_logs.job_type IS 'Type of cron job (morning_report, queue_process, etc.)';
COMMENT ON COLUMN public.cron_logs.duration_ms IS 'Execution duration in milliseconds';

-- ============================================================================
-- Step 3: Sessions Table
-- ============================================================================
-- Tracks user sessions for cleanup and analytics
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,

    -- Session data
    token_hash TEXT NOT NULL,
    device_info JSONB,
    ip_address TEXT,
    user_agent TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMPTZ
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user ON public.sessions(tenant_id, user_id, last_active DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON public.sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON public.sessions(is_active, expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_cleanup ON public.sessions(last_active) WHERE is_active = TRUE;

COMMENT ON TABLE public.sessions IS 'User session tracking for auth and cleanup';
COMMENT ON COLUMN public.sessions.token_hash IS 'Hashed session token for security';

-- Enable RLS for sessions
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sessions_tenant_isolation"
ON public.sessions
FOR SELECT
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

CREATE POLICY "sessions_own_sessions"
ON public.sessions
FOR ALL
USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- ============================================================================
-- Step 4: Refresh Tokens Table
-- ============================================================================
-- Tracks refresh tokens for token renewal
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,

    -- Token data
    token_hash TEXT NOT NULL UNIQUE,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,

    -- Status
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    revoke_reason TEXT
);

-- Indexes for refresh_tokens
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON public.refresh_tokens(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON public.refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_session ON public.refresh_tokens(session_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_cleanup ON public.refresh_tokens(expires_at) WHERE is_revoked = FALSE;

COMMENT ON TABLE public.refresh_tokens IS 'Refresh tokens for session renewal';
COMMENT ON COLUMN public.refresh_tokens.token_hash IS 'Hashed refresh token for security';

-- Enable RLS for refresh_tokens
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "refresh_tokens_own_tokens"
ON public.refresh_tokens
FOR ALL
USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- ============================================================================
-- Step 5: API Keys Table
-- ============================================================================
-- Tracks API keys for programmatic access
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,

    -- Key data
    key_hash TEXT NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL,  -- First 8 chars for identification
    name TEXT NOT NULL,
    description TEXT,

    -- Permissions
    scopes JSONB DEFAULT '["read"]'::jsonb,

    -- Usage limits
    rate_limit INTEGER DEFAULT 1000,  -- Requests per hour
    monthly_limit INTEGER DEFAULT 100000,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMPTZ
);

-- Indexes for api_keys
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON public.api_keys(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON public.api_keys(key_prefix);

COMMENT ON TABLE public.api_keys IS 'API keys for programmatic access';
COMMENT ON COLUMN public.api_keys.key_prefix IS 'First 8 characters of key for identification';

-- Enable RLS for api_keys
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "api_keys_own_keys"
ON public.api_keys
FOR ALL
USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- ============================================================================
-- Step 6: Rate Limit Tracking Table
-- ============================================================================
-- Tracks API rate limiting per user/key
CREATE TABLE IF NOT EXISTS public.rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identity
    tenant_id TEXT NOT NULL,
    user_id TEXT,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE CASCADE,
    ip_address TEXT,

    -- Rate limit window
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,

    -- Counts
    request_count INTEGER DEFAULT 0,
    blocked_count INTEGER DEFAULT 0,

    -- Metadata
    endpoint_pattern TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for rate_limits
CREATE INDEX IF NOT EXISTS idx_rate_limits_lookup ON public.rate_limits(tenant_id, user_id, window_start);
CREATE INDEX IF NOT EXISTS idx_rate_limits_api_key ON public.rate_limits(api_key_id, window_start);
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON public.rate_limits(ip_address, window_start);
CREATE INDEX IF NOT EXISTS idx_rate_limits_cleanup ON public.rate_limits(window_end);

COMMENT ON TABLE public.rate_limits IS 'API rate limiting tracking';

-- ============================================================================
-- Step 7: Audit Log Table
-- ============================================================================
-- Tracks sensitive operations for compliance
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Multi-tenant identity
    tenant_id TEXT NOT NULL,
    user_id TEXT,
    api_key_id UUID,

    -- Event details
    event_type TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    action TEXT NOT NULL,  -- 'create', 'read', 'update', 'delete'

    -- Request context
    ip_address TEXT,
    user_agent TEXT,
    request_id TEXT,

    -- Event data
    old_values JSONB,
    new_values JSONB,
    metadata JSONB,

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON public.audit_logs(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON public.audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON public.audit_logs(resource_type, resource_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON public.audit_logs(event_type, created_at DESC);

COMMENT ON TABLE public.audit_logs IS 'Audit trail for sensitive operations';

-- Enable RLS for audit_logs
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "audit_logs_tenant_read"
ON public.audit_logs
FOR SELECT
USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');

-- ============================================================================
-- Step 8: Helper Functions for Database Introspection
-- ============================================================================

-- Function to get PostgreSQL version
CREATE OR REPLACE FUNCTION public.get_pg_version()
RETURNS TEXT AS $$
BEGIN
    RETURN version();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get table info
CREATE OR REPLACE FUNCTION public.get_table_info()
RETURNS TABLE (
    table_schema TEXT,
    table_name TEXT,
    row_count BIGINT,
    has_rls BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.table_schema::TEXT,
        t.table_name::TEXT,
        (SELECT reltuples::BIGINT FROM pg_class WHERE oid = (t.table_schema || '.' || t.table_name)::regclass),
        (SELECT rowsecurity FROM pg_class WHERE oid = (t.table_schema || '.' || t.table_name)::regclass)
    FROM information_schema.tables t
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get extensions
CREATE OR REPLACE FUNCTION public.get_extensions()
RETURNS TABLE (extname TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT e.extname::TEXT FROM pg_extension e ORDER BY e.extname;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get table columns
CREATE OR REPLACE FUNCTION public.get_table_columns(p_table_name TEXT)
RETURNS TABLE (
    column_name TEXT,
    data_type TEXT,
    is_nullable TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.column_name::TEXT,
        c.data_type::TEXT,
        c.is_nullable::TEXT
    FROM information_schema.columns c
    WHERE c.table_schema = 'public'
    AND c.table_name = p_table_name
    ORDER BY c.ordinal_position;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get table indexes
CREATE OR REPLACE FUNCTION public.get_table_indexes(p_table_name TEXT)
RETURNS TABLE (indexname TEXT, indexdef TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.indexname::TEXT,
        i.indexdef::TEXT
    FROM pg_indexes i
    WHERE i.schemaname = 'public'
    AND i.tablename = p_table_name
    ORDER BY i.indexname;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if table has RLS
CREATE OR REPLACE FUNCTION public.check_table_rls(p_table_name TEXT)
RETURNS TABLE (has_rls BOOLEAN) AS $$
BEGIN
    RETURN QUERY
    SELECT rowsecurity FROM pg_class WHERE relname = p_table_name AND relnamespace = 'public'::regnamespace;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to execute SQL (admin only)
CREATE OR REPLACE FUNCTION public.exec_sql(sql TEXT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    EXECUTE sql;
    RETURN jsonb_build_object('success', true);
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('success', false, 'error', SQLERRM);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Tables created:
-- 1. schema_migrations - Migration tracking
-- 2. cron_logs - Cron job execution logs
-- 3. sessions - User session tracking
-- 4. refresh_tokens - Token renewal tracking
-- 5. api_keys - API key management
-- 6. rate_limits - Rate limiting tracking
-- 7. audit_logs - Audit trail
--
-- Functions created:
-- - get_pg_version() - PostgreSQL version
-- - get_table_info() - Table list with RLS status
-- - get_extensions() - Installed extensions
-- - get_table_columns() - Table column info
-- - get_table_indexes() - Table index info
-- - check_table_rls() - RLS check
-- - exec_sql() - SQL execution (admin)
