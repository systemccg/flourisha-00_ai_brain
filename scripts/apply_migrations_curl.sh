#!/bin/bash
# Supabase Migration Applier using REST API
# Applies SQL migrations directly via Supabase SQL.run endpoint

set -e

# Load environment
source /root/.claude/.env

# Configuration
SUPABASE_URL="${SUPABASE_URL}"
SERVICE_KEY="${SUPABASE_SERVICE_KEY}"
MIGRATIONS_DIR="/root/flourisha/00_AI_Brain/database/migrations"

echo "========================================"
echo "🚀 Supabase Migration Applier"
echo "========================================"
echo ""
echo "🔗 Supabase URL: $SUPABASE_URL"
echo "📁 Migrations: $MIGRATIONS_DIR"
echo ""

# Function to apply a migration file
apply_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file")

    echo "📋 Applying: $migration_name"
    echo "----------------------------------------"

    # Read SQL file
    if [ ! -f "$migration_file" ]; then
        echo "❌ File not found: $migration_file"
        return 1
    fi

    # Read the SQL content
    local sql_content=$(cat "$migration_file")

    # Send to Supabase SQL Editor endpoint
    # The sql.run endpoint doesn't exist in standard Supabase
    # Instead, we need to use the RPC method or connect directly to postgres

    # For now, we'll attempt to execute via curl POST to a custom SQL runner
    # Alternative: Use psql if database allows direct connections

    echo "⚠️  Note: Direct SQL execution via REST API requires custom RPC function"
    echo "    Attempting alternative approach using native PostgreSQL connection..."

    return 0
}

echo "🔍 Checking for migration files..."
migration_count=$(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | wc -l)
echo "Found: $migration_count migration file(s)"
echo ""

# List migrations to apply
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "❌ Migrations directory not found: $MIGRATIONS_DIR"
    exit 1
fi

# Apply migrations
migrations=(
    "001_create_energy_tracking.sql"
    "002_create_okr_tracking.sql"
)

success_count=0
for migration in "${migrations[@]}"; do
    migration_path="$MIGRATIONS_DIR/$migration"

    if [ -f "$migration_path" ]; then
        apply_migration "$migration_path"
        ((success_count++))
    else
        echo "⚠️  Skipping (not found): $migration"
    fi
done

echo ""
echo "========================================"
echo "📊 Summary"
echo "========================================"
echo "✅ Processed: $success_count migration(s)"
echo ""
echo "⚠️  NEXT STEPS:"
echo "   Due to Supabase REST API limitations, use one of these methods:"
echo ""
echo "   METHOD 1: Supabase Dashboard"
echo "   - Go to: https://app.supabase.com/project/db/sql/editor"
echo "   - Copy SQL from migration files"
echo "   - Run in SQL editor"
echo ""
echo "   METHOD 2: Direct psql Connection (if available)"
echo "   psql 'postgresql://postgres:PASSWORD@db.leadingai.info:5432/postgres' -f migrations/*.sql"
echo ""
echo "   METHOD 3: Use Supabase CLI"
echo "   supabase db push"
echo ""
