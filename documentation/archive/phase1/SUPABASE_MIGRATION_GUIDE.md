# Supabase Migration Guide - Phase 1

**Date:** 2025-12-06
**Status:** Ready for Migration
**Migrations:** 2 (energy_tracking, okr_tracking)

---

## Executive Summary

Two database migrations need to be applied to Supabase to complete Phase 1 of the Flourisha AI Brain system:

1. **001_create_energy_tracking.sql** - Energy and focus tracking data (90-minute intervals)
2. **002_create_okr_tracking.sql** - Quarterly OKR tracking with progress measurement

Both migrations include:
- Table creation with proper indexes
- Row-Level Security (RLS) policies for multi-tenant isolation
- Helper functions for analytics
- Sample data for testing

---

## Migration Files Location

```
/root/flourisha/00_AI_Brain/database/migrations/
├── 001_create_energy_tracking.sql   (186 lines)
└── 002_create_okr_tracking.sql      (427 lines)
```

---

## Method 1: Supabase Dashboard (Easiest)

**For users who prefer visual interface**

### Step 1: Access Supabase Dashboard

1. Open browser: https://app.supabase.com
2. Sign in to your Supabase account
3. Select project: `leadingai`
4. Navigate to: **SQL Editor** (left sidebar)

### Step 2: Create First Migration

1. Click **New Query**
2. Copy content from `/root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql`
3. Paste into editor
4. Click **Run** button
5. Wait for success notification: "✅ Energy tracking schema created successfully!"

### Step 3: Create Second Migration

1. Click **New Query** again
2. Copy content from `/root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql`
3. Paste into editor
4. Click **Run** button
5. Wait for success notification: "✅ OKR tracking schema created successfully!"

### Step 4: Verify Success

Click **Tables** in left sidebar - you should see:
- `public.energy_tracking` (new table)
- `public.okr_tracking` (new table)

---

## Method 2: Supabase CLI (Recommended for Automation)

**For users with Supabase CLI installed**

### Prerequisites

```bash
# Install Supabase CLI
curl -fsSL https://cli.supabase.io/install.sh | sh

# Or with bun
bun install -g supabase
```

### Step 1: Link Local Project to Supabase

```bash
cd /root/flourisha/00_AI_Brain

# Login to Supabase
supabase login

# Link to remote project
supabase link --project-ref db
```

### Step 2: Push Migrations

```bash
# Apply all migrations
supabase db push

# Or specific migration
supabase db push migrations/001_create_energy_tracking.sql
```

### Step 3: Verify

```bash
# List all tables
supabase db tables

# Check specific table
supabase db info energy_tracking
```

---

## Method 3: Direct PostgreSQL Connection (Advanced)

**For users with psql access and password**

### Prerequisites

Supabase PostgreSQL password (not included in .env - requires manual entry)

### Step 1: Connect to Supabase PostgreSQL

```bash
# Use Supabase connection details
psql -h db.leadingai.info \
     -U postgres \
     -d postgres \
     -p 5432
```

When prompted, enter your Supabase database password.

### Step 2: Run Migrations

```sql
-- Execute migration 1
\i /root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql

-- Execute migration 2
\i /root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql

-- Verify tables exist
\dt public.energy_tracking
\dt public.okr_tracking
```

---

## Verification Queries

After migrations are applied, run these queries to verify success:

### 1. Energy Tracking Table

```sql
-- Should return the table structure
\d public.energy_tracking

-- Should return 0 (no data yet, or sample data if included)
SELECT COUNT(*) as total_rows FROM public.energy_tracking;

-- Verify indexes
SELECT indexname FROM pg_indexes
WHERE tablename = 'energy_tracking';

-- Check RLS policies
SELECT policyname FROM pg_policies
WHERE tablename = 'energy_tracking';
```

### 2. OKR Tracking Table

```sql
-- Should return the table structure
\d public.okr_tracking

-- Should return 13 (sample OKRs included)
SELECT COUNT(*) as total_okrs FROM public.okr_tracking;

-- Verify indexes
SELECT indexname FROM pg_indexes
WHERE tablename = 'okr_tracking';

-- Check RLS policies
SELECT policyname FROM pg_policies
WHERE tablename = 'okr_tracking';
```

### 3. Helper Functions

```sql
-- Check if functions exist
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name LIKE '%energy%' OR routine_name LIKE '%okr%';

-- Test energy tracking function (if sample data exists)
SELECT * FROM get_average_energy_for_period(
    'cocreators_group',
    'kai_user_id',
    NOW() - INTERVAL '1 day',
    NOW()
);
```

---

## Troubleshooting

### Error: "relation 'public.tenants' does not exist"

**Cause:** The migrations reference a `tenants` table that doesn't exist yet.

**Solution:**
```sql
-- First check if tenants table exists
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'tenants'
);

-- If not, create basic tenants table
CREATE TABLE IF NOT EXISTS public.tenants (
    tenant_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Error: "function update_updated_at_column does not exist"

**Cause:** Helper function referenced but not created.

**Solution:**
```sql
-- Create the trigger function if missing
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Error: "policy already exists"

**Cause:** RLS policies already created in previous attempt.

**Solution:** This is safe to ignore - migrations use `CREATE POLICY IF NOT EXISTS`

### Error: "index already exists"

**Cause:** Indexes already created.

**Solution:** Migrations use `CREATE INDEX IF NOT EXISTS` - safe to ignore

### Error: "constraint violation on tenants foreign key"

**Cause:** Sample data references non-existent tenant.

**Solution:**
1. Remove sample data section from migration SQL
2. Or create tenant first:
```sql
INSERT INTO public.tenants (tenant_id) VALUES ('cocreators_group');
```

---

## Post-Migration Steps

### 1. Install Python Dependencies

```bash
# For morning report scripts
uv pip install --system \
    supabase \
    pyyaml \
    python-dotenv \
    aiohttp \
    asyncpg
```

### 2. Test Morning Report Generator

```bash
# Test migration data is accessible
python3 /root/flourisha/00_AI_Brain/scripts/morning-report-generator.py --test

# Should output:
# ✅ Database connection: OK
# ✅ OKR tracking: 13 records
# ✅ Energy tracking: 4 sample records
```

### 3. Verify Cron Jobs

```bash
# Check cron jobs are registered
crontab -l | grep flourisha

# Should show:
# 0 7 * * * /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/morning-report-generator.py
# 0 */4 * * * /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/para-analyzer.py
```

### 4. Check Hook Registration

```bash
# Verify evening hook is registered
grep -A 2 "evening-productivity-analysis" /root/.claude/settings.json

# Should show SessionEnd trigger
```

---

## Monitoring

After migrations are applied, monitor these for issues:

### Database Size

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### RLS Policy Status

```sql
-- Verify RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('energy_tracking', 'okr_tracking');

-- Should show: rowsecurity = t (true)
```

### Index Usage

```sql
-- Monitor index efficiency
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## Rollback Procedure

If migrations need to be rolled back:

```sql
-- Drop tables (all data will be lost)
DROP TABLE IF EXISTS public.okr_tracking CASCADE;
DROP TABLE IF EXISTS public.energy_tracking CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS get_average_energy_for_period(TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ) CASCADE;
DROP FUNCTION IF EXISTS calculate_okr_progress(TEXT, TEXT, TEXT) CASCADE;
DROP FUNCTION IF EXISTS get_at_risk_okrs(TEXT, TEXT, INTEGER) CASCADE;
```

---

## Next Steps

After migrations are successfully applied:

1. **Phase 2: Energy Tracking** (Week 2)
   - Build Chrome extension
   - Configure Twilio for SMS
   - Test 90-minute tracking intervals

2. **Phase 3: Knowledge Intelligence** (Week 3)
   - Create personality_profiles table (Neo4j)
   - Implement email labeling service
   - Build email response agent

3. **Phase 4: System Evolution** (Week 4)
   - Implement agent_factory.py
   - Setup continuous improvement loop
   - Test temporal agent creation

---

## Support

**Issues with migrations?**

Check the comprehensive guide: `/root/flourisha/00_AI_Brain/DATABASE_MIGRATION_GUIDE.md`

**Questions about the system?**

- Architecture: `/root/flourisha/00_AI_Brain/documentation/FOUR_DEPARTMENT_SYSTEM.md`
- OKR System: `/root/flourisha/00_AI_Brain/documentation/services/OKR_SYSTEM.md`
- Morning Report: `/root/flourisha/00_AI_Brain/documentation/services/MORNING_REPORT.md`
- Energy Tracking: `/root/flourisha/00_AI_Brain/documentation/services/ENERGY_TRACKING.md`

---

**Status:** Ready for Migration
**Last Updated:** 2025-12-06
**Estimated Time:** 5 minutes
**Risk Level:** Low (reversible migrations with IF NOT EXISTS clauses)
