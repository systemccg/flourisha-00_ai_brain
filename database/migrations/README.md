# Flourisha AI Brain Database Migrations

## Overview

This directory contains database migrations for the Flourisha AI Brain Phase 1 implementation. These migrations extend the existing Content Intelligence schema with productivity tracking capabilities.

## Migration Files

### 001_create_energy_tracking.sql
**Purpose**: Track energy levels and focus quality every 90 minutes

**Tables Created**:
- `energy_tracking` - Stores user energy readings (1-10 scale) and focus quality (deep/shallow/distracted)

**Key Features**:
- Multi-tenant isolation with RLS policies
- Indexes for efficient time-based queries
- Helper function: `get_average_energy_for_period()` for analytics
- Sample data for testing

**Dependencies**: Requires `tenants` table from base schema

### 002_create_okr_tracking.sql
**Purpose**: Track quarterly Objectives and Key Results (OKRs) with progress monitoring

**Tables Created**:
- `okr_tracking` - Stores objectives, key results, targets, current progress, and status

**Key Features**:
- Multi-tenant isolation with RLS policies
- Hierarchical structure: Quarter → Objective → Key Results
- Helper functions:
  - `calculate_okr_progress()` - Calculate completion percentage and status distribution
  - `get_at_risk_okrs()` - Identify OKRs approaching deadline with low progress
- Sample data: 4 Q1 2026 objectives with 13 key results

**Dependencies**: Requires `tenants` table from base schema

### 003_extraction_feedback.sql
**Purpose**: Track feedback on document extraction quality

**Dependencies**: Requires `processed_content` table from base schema

### 004_okr_visibility_and_tags.sql
**Purpose**: Add personal/workspace visibility model and tagging support for OKRs

**New Columns on okr_tracking**:
- `user_id` (UUID) - Owner for personal OKRs
- `visibility` (VARCHAR) - 'personal' or 'workspace'
- `workspace_id` (UUID) - For future workspace support
- `priority` (INTEGER) - For sorting
- `department` (VARCHAR) - For grouping by department

**Tables Created**:
- `okr_tags` - Personal and workspace-scoped tags for organizing OKRs
- `okr_objective_tags` - Junction table linking OKRs to tags
- `okr_progress_history` - Historical record of OKR progress changes

**Key Features**:
- Visibility model: personal OKRs span all workspaces, workspace OKRs visible to members
- Tagging system with colors for organization
- Progress history for trending and analysis
- Updated RLS policies for visibility model
- Helper function: `get_user_okr_overview()` - Get OKR summary across contexts

**Dependencies**: Requires `okr_tracking` table from migration 002

## Migration Sequence

These migrations should be run **after** the base Content Intelligence schema (`01_content_intelligence_schema.sql`):

1. Base schema (existing):
   - `01_content_intelligence_schema.sql` - Creates tenants, projects, processed_content, etc.
   - `02_add_embeddings.sql` - Adds pgvector support

2. AI Brain migrations (new):
   - `001_create_energy_tracking.sql` - Energy and focus tracking
   - `002_create_okr_tracking.sql` - OKR progress tracking

## Running Migrations

### Via Supabase Dashboard
1. Navigate to SQL Editor in Supabase Dashboard
2. Copy contents of migration file
3. Execute SQL
4. Verify success messages in output

### Via Supabase CLI
```bash
# Apply all migrations
supabase db push

# Or apply specific migration
psql $DATABASE_URL -f 001_create_energy_tracking.sql
psql $DATABASE_URL -f 002_create_okr_tracking.sql
```

### Via psql
```bash
# Connect to database
psql -h your-host -U postgres -d your-database

# Run migration
\i /root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql
\i /root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql
```

## Verification

After running migrations, verify tables and policies:

```sql
-- Check tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('energy_tracking', 'okr_tracking');

-- Check RLS policies
SELECT tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename IN ('energy_tracking', 'okr_tracking');

-- Test sample data
SELECT COUNT(*) FROM energy_tracking;
SELECT COUNT(*) FROM okr_tracking;

-- Test helper functions
SELECT * FROM get_average_energy_for_period(
    'cocreators_group',
    'kai_user_id',
    NOW() - INTERVAL '1 day',
    NOW()
);

SELECT * FROM calculate_okr_progress('cocreators_group', 'Q1_2026', NULL);
SELECT * FROM get_at_risk_okrs('cocreators_group', 'Q1_2026', 30);
```

## Schema Standards

All migrations follow Flourisha schema standards:

### Required Elements
- ✅ UUID primary keys with `uuid_generate_v4()`
- ✅ `tenant_id` foreign key to `tenants(tenant_id)`
- ✅ Timestamps: `created_at`, `updated_at` (where applicable)
- ✅ Row Level Security (RLS) enabled
- ✅ RLS policies for tenant isolation
- ✅ Proper indexes for query performance
- ✅ Table and column comments for documentation
- ✅ Sample data for testing

### Naming Conventions
- Tables: `snake_case`, plural or descriptive (e.g., `energy_tracking`, `okr_tracking`)
- Columns: `snake_case`
- Indexes: `idx_<table>_<columns>` (e.g., `idx_energy_tenant_time`)
- Functions: `snake_case` with descriptive names
- Constraints: `CHECK` constraints for data validation

## Integration with Evening Hook

The `evening-productivity-analysis.ts` hook (in `/root/flourisha/00_AI_Brain/hooks/`) will:

1. Run after SessionEnd events (after 5 PM)
2. Analyze session data and calculate productivity metrics
3. Generate daily analysis JSON file
4. **Future**: Query `energy_tracking` table for energy pattern analysis
5. **Future**: Update `okr_tracking` table with progress made during session

## Rollback

If you need to rollback these migrations:

```sql
-- Drop tables (cascades to dependent objects)
DROP TABLE IF EXISTS public.energy_tracking CASCADE;
DROP TABLE IF EXISTS public.okr_tracking CASCADE;

-- Drop helper functions
DROP FUNCTION IF EXISTS get_average_energy_for_period;
DROP FUNCTION IF EXISTS calculate_okr_progress;
DROP FUNCTION IF EXISTS get_at_risk_okrs;
```

## Next Steps

1. ✅ Apply migrations to Supabase database
2. ✅ Verify tables and policies created successfully
3. ✅ Test helper functions with sample data
4. Configure evening hook in Claude Code settings.json
5. Build UI for energy tracking input (Chrome extension / SMS)
6. Build UI for OKR management and progress updates
7. Integrate hook with database for automated tracking
8. Create morning report generator to consume daily analysis

## Support

For issues or questions about these migrations, contact the engineering team or refer to:
- Flourisha documentation: `/root/flourisha/00_AI_Brain/documentation/`
- Base schema: `/root/flourisha/00_AI_Brain/database/01_content_intelligence_schema.sql`
