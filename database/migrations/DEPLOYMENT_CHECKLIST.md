# Flourisha AI Brain Phase 1 - Deployment Checklist

## Files Created

### Database Migrations
- ✅ `/root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql` (186 lines)
- ✅ `/root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql` (427 lines)
- ✅ `/root/flourisha/00_AI_Brain/database/migrations/README.md` (Documentation)

### Hook System
- ✅ `/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts` (582 lines)
- ✅ `/root/flourisha/00_AI_Brain/hooks/HOOK_REGISTRATION.md` (Hook setup guide)

### Directory Structure
- ✅ `/root/flourisha/00_AI_Brain/history/daily-analysis/` (Output directory)

## Pre-Deployment Verification

### 1. Database Prerequisites

#### Check Supabase Connection
```bash
# Verify Supabase project is accessible
# Replace with your project details
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

#### Verify Base Schema
```sql
-- Ensure base tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('tenants', 'projects', 'processed_content');

-- Expected: 3 rows returned
```

#### Verify Extensions
```sql
-- Check UUID extension
SELECT * FROM pg_extension WHERE extname = 'uuid-ossp';

-- Check pgvector extension (for embeddings)
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 2. Migration Execution Plan

#### Step 1: Review SQL Files
```bash
# Review energy tracking migration
less /root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql

# Review OKR tracking migration
less /root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql
```

#### Step 2: Apply Migrations (Supabase Dashboard)
1. Log into Supabase Dashboard
2. Navigate to SQL Editor
3. Create new query
4. Copy contents of `001_create_energy_tracking.sql`
5. Execute
6. Verify success messages
7. Repeat for `002_create_okr_tracking.sql`

#### Step 3: Apply Migrations (CLI)
```bash
# Using psql
cd /root/flourisha/00_AI_Brain/database/migrations

psql $DATABASE_URL -f 001_create_energy_tracking.sql
psql $DATABASE_URL -f 002_create_okr_tracking.sql
```

#### Step 4: Verify Tables Created
```sql
-- List new tables
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('energy_tracking', 'okr_tracking');

-- Check row counts (should have sample data)
SELECT 'energy_tracking' as table_name, COUNT(*) FROM energy_tracking
UNION ALL
SELECT 'okr_tracking', COUNT(*) FROM okr_tracking;
```

#### Step 5: Verify Indexes
```sql
-- Check energy_tracking indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'energy_tracking';

-- Check okr_tracking indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'okr_tracking';
```

#### Step 6: Verify RLS Policies
```sql
-- Check energy_tracking policies
SELECT policyname, cmd, qual
FROM pg_policies
WHERE tablename = 'energy_tracking';

-- Check okr_tracking policies
SELECT policyname, cmd, qual
FROM pg_policies
WHERE tablename = 'okr_tracking';
```

#### Step 7: Test Helper Functions
```sql
-- Test energy tracking analytics
SELECT * FROM get_average_energy_for_period(
    'cocreators_group',
    'kai_user_id',
    NOW() - INTERVAL '1 day',
    NOW()
);

-- Test OKR progress calculation
SELECT * FROM calculate_okr_progress(
    'cocreators_group',
    'Q1_2026',
    NULL
);

-- Test at-risk OKR detection
SELECT * FROM get_at_risk_okrs(
    'cocreators_group',
    'Q1_2026',
    30
);
```

### 3. Hook System Setup

#### Step 1: Verify Hook File
```bash
# Check file exists and is executable
ls -lah /root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts

# Should show: -rwxr-xr-x (executable permissions)
```

#### Step 2: Install Dependencies (if needed)
```bash
# Check if Node.js is available
node --version

# Check if TypeScript is available (for ts-node)
npx ts-node --version
```

#### Step 3: Test Hook Manually
```bash
# Run hook directly
cd /root/flourisha/00_AI_Brain/hooks
node evening-productivity-analysis.ts

# Check output
cat /root/flourisha/00_AI_Brain/history/daily-analysis/$(date +%Y-%m-%d).json
```

#### Step 4: Register Hook in Claude Code

**Location**: `~/.config/claude-code/settings.json` (or your Claude Code config path)

**Add this configuration**:
```json
{
  "hooks": [
    {
      "trigger": "SessionEnd",
      "condition": "timeOfDay >= 17:00",
      "script": "/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts",
      "description": "Generate evening productivity analysis after 5 PM sessions",
      "enabled": true
    }
  ]
}
```

#### Step 5: Verify Hook Registration
```bash
# Check Claude Code config
cat ~/.config/claude-code/settings.json | grep -A 6 "evening-productivity"

# Restart Claude Code if needed
```

### 4. Validation Tests

#### Test 1: Energy Tracking Insert
```sql
-- Insert test energy reading
INSERT INTO energy_tracking (
    tenant_id,
    user_id,
    timestamp,
    energy_level,
    focus_quality,
    source,
    notes
) VALUES (
    'cocreators_group',
    'test_user',
    NOW(),
    8,
    'deep',
    'manual',
    'Test reading from deployment validation'
);

-- Verify inserted
SELECT * FROM energy_tracking
WHERE notes LIKE '%deployment validation%';
```

#### Test 2: OKR Progress Update
```sql
-- Update KR progress
UPDATE okr_tracking
SET key_result_current = 1
WHERE tenant_id = 'cocreators_group'
AND quarter = 'Q1_2026'
AND objective_id = 'OBJ-001'
AND key_result_id = 'KR-002';

-- Verify updated
SELECT objective_id, key_result_id, key_result_current, last_updated
FROM okr_tracking
WHERE objective_id = 'OBJ-001' AND key_result_id = 'KR-002';
```

#### Test 3: RLS Tenant Isolation
```sql
-- Attempt to insert with wrong tenant (should fail with RLS)
-- This test requires proper JWT token setup

-- Set tenant context
SET request.jwt.claims = '{"tenant_id": "wrong_tenant", "sub": "test_user"}';

-- Try to query (should return empty)
SELECT * FROM energy_tracking;

-- Reset to correct tenant
SET request.jwt.claims = '{"tenant_id": "cocreators_group", "sub": "kai_user_id"}';

-- Should return data now
SELECT COUNT(*) FROM energy_tracking;
```

#### Test 4: Hook Output Validation
```bash
# Check JSON structure
cat /root/flourisha/00_AI_Brain/history/daily-analysis/$(date +%Y-%m-%d).json | jq .

# Expected keys:
# - date
# - productivityScore
# - hoursWorked
# - accomplishments
# - toolsUsed
# - projectsWorkedOn
# - etc.
```

## Post-Deployment Verification

### Database Health Check
```sql
-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename IN ('energy_tracking', 'okr_tracking')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
WHERE tablename IN ('energy_tracking', 'okr_tracking')
ORDER BY idx_scan DESC;
```

### Performance Benchmarks
```sql
-- Test query performance
EXPLAIN ANALYZE
SELECT * FROM energy_tracking
WHERE tenant_id = 'cocreators_group'
AND timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;

-- Should use idx_energy_tenant_time index
-- Execution time should be < 50ms
```

### Security Audit
```sql
-- Verify RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE tablename IN ('energy_tracking', 'okr_tracking');

-- Both should show: rowsecurity = true

-- Verify policies exist
SELECT COUNT(*) as policy_count
FROM pg_policies
WHERE tablename IN ('energy_tracking', 'okr_tracking');

-- Should return: policy_count >= 5 (at least 5 policies total)
```

## Rollback Plan

If deployment fails or issues are found:

### Emergency Rollback
```sql
-- Drop new tables
DROP TABLE IF EXISTS public.energy_tracking CASCADE;
DROP TABLE IF EXISTS public.okr_tracking CASCADE;

-- Drop helper functions
DROP FUNCTION IF EXISTS get_average_energy_for_period;
DROP FUNCTION IF EXISTS calculate_okr_progress;
DROP FUNCTION IF EXISTS get_at_risk_okrs;
```

### Disable Hook
```bash
# Edit Claude Code settings.json
# Change "enabled": true to "enabled": false

# Or remove hook configuration entirely
```

## Success Criteria

### Database Migrations
- ✅ Tables created: `energy_tracking`, `okr_tracking`
- ✅ Indexes created and used
- ✅ RLS policies active
- ✅ Helper functions working
- ✅ Sample data inserted
- ✅ Query performance < 50ms

### Hook System
- ✅ Hook file executable
- ✅ Hook registered in Claude Code
- ✅ Time condition working (only after 5 PM)
- ✅ JSON output generated correctly
- ✅ Directory structure created
- ✅ Error handling working

### Integration
- ✅ Hook can read session logs
- ✅ Productivity metrics calculated
- ✅ Patterns detected correctly
- ✅ JSON consumable by morning report

## Next Steps After Deployment

1. Monitor hook execution for first week
2. Review generated daily analysis files
3. Build morning report generator integration
4. Create energy tracking input UI (Chrome extension)
5. Build OKR management dashboard
6. Add database integration to hook (query energy_tracking)
7. Add OKR progress auto-update from hook
8. Set up automated backups for daily analysis files
9. Create analytics dashboard for productivity trends
10. Integrate with notification system for at-risk OKRs

## Support & Troubleshooting

### Common Issues

**Issue**: Table creation fails
- **Solution**: Check that base schema is deployed first
- **Solution**: Verify `tenants` table exists

**Issue**: RLS policies fail
- **Solution**: Ensure JWT claims format matches expectations
- **Solution**: Check Supabase Auth is configured

**Issue**: Hook doesn't run
- **Solution**: Verify time is >= 17:00
- **Solution**: Check hook is enabled in settings.json
- **Solution**: Verify file permissions (chmod +x)

**Issue**: No JSON output
- **Solution**: Check directory permissions on `/root/flourisha/00_AI_Brain/history/`
- **Solution**: Check disk space
- **Solution**: Review hook error logs

### Logs & Monitoring

```bash
# Check hook execution logs
tail -f /var/log/claude-code/hooks.log

# Check daily analysis files
ls -lah /root/flourisha/00_AI_Brain/history/daily-analysis/

# Check database logs (Supabase Dashboard)
# Navigate to: Logs → Database Logs
```

## Documentation Links

- **Migration README**: `/root/flourisha/00_AI_Brain/database/migrations/README.md`
- **Hook Registration**: `/root/flourisha/00_AI_Brain/hooks/HOOK_REGISTRATION.md`
- **Base Schema**: `/root/flourisha/00_AI_Brain/database/01_content_intelligence_schema.sql`
- **Flourisha Docs**: `/root/flourisha/00_AI_Brain/documentation/`

## Sign-Off

- [ ] Database migrations reviewed and tested
- [ ] Hook implementation reviewed and tested
- [ ] RLS policies verified secure
- [ ] Performance benchmarks acceptable
- [ ] Documentation complete
- [ ] Rollback plan documented
- [ ] Ready for production deployment

**Deployed by**: _________________
**Date**: _________________
**Version**: Phase 1 - Initial Release
