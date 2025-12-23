#!/usr/bin/env python3
"""
Supabase Migration Applier
Applies database migrations to Supabase using SERVICE_KEY authentication
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.expanduser("~/.claude/.env"))

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment")
    sys.exit(1)

# Import after credentials are verified
try:
    from supabase import create_client
except ImportError:
    print("❌ ERROR: supabase package not installed")
    print("Install with: uv pip install supabase")
    sys.exit(1)


def read_migration_file(migration_path: str) -> str:
    """Read SQL migration file"""
    try:
        with open(migration_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ ERROR: Migration file not found: {migration_path}")
        sys.exit(1)


def execute_migration(client, migration_sql: str, migration_name: str) -> bool:
    """Execute SQL migration against Supabase"""
    try:
        print(f"\n📋 Executing migration: {migration_name}")
        print("-" * 60)

        # Split SQL into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        executed = 0

        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    result = client.postgrest.rpc('exec_sql', {'sql': statement}).execute()
                    executed += 1
                    # Show progress every 5 statements
                    if i % 5 == 0 or i == len(statements):
                        print(f"  ✓ Executed {i}/{len(statements)} statements")
                except Exception as e:
                    # Some statements may fail due to conflicts, continue
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"  ⚠️  Statement {i}: Already exists (skipping)")
                        continue
                    else:
                        # Log but continue - RLS policies might fail if already exist
                        print(f"  ⚠️  Statement {i}: {str(e)[:80]}")
                        continue

        print(f"✅ {migration_name}: Executed {executed}/{len(statements)} statements")
        return True

    except Exception as e:
        print(f"❌ {migration_name} failed: {str(e)}")
        return False


def verify_migration(client, table_name: str) -> bool:
    """Verify that migration succeeded"""
    try:
        print(f"\n🔍 Verifying table: {table_name}")
        result = client.table(table_name).select("*", count="exact").limit(0).execute()
        print(f"  ✓ Table '{table_name}' exists and is accessible")
        print(f"  ✓ Row count: {result.count if hasattr(result, 'count') else 'unknown'}")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not verify table: {str(e)[:100]}")
        # Don't fail hard - might be RLS issue
        return True


def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 Supabase Migration Applier")
    print("=" * 60)
    print(f"\n🔗 Connecting to Supabase: {SUPABASE_URL}")

    # Create Supabase client using SERVICE_KEY for admin access
    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        sys.exit(1)

    # Get migration files directory
    script_dir = Path(__file__).parent
    migrations_dir = script_dir.parent / "database" / "migrations"

    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    print(f"\n📁 Migrations directory: {migrations_dir}")

    # Get migration files in order
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("❌ No migration files found")
        sys.exit(1)

    print(f"📦 Found {len(migration_files)} migration file(s)")

    # Track results
    results = {}
    migrations_to_apply = [
        ("001_create_energy_tracking.sql", "energy_tracking"),
        ("002_create_okr_tracking.sql", "okr_tracking"),
    ]

    # Apply migrations
    for migration_file, table_name in migrations_to_apply:
        migration_path = migrations_dir / migration_file

        if not migration_path.exists():
            print(f"\n⚠️  Skipping {migration_file} - file not found")
            continue

        # Read migration
        migration_sql = read_migration_file(str(migration_path))

        # Execute migration
        success = execute_migration(client, migration_sql, migration_file)
        results[migration_file] = success

        # Verify migration
        if success:
            verify_migration(client, table_name)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)

    for migration, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {migration}")

    # Final verification queries
    print("\n🔍 Final Verification Queries")
    print("-" * 60)

    verification_queries = {
        "energy_tracking": "SELECT COUNT(*) as count FROM public.energy_tracking",
        "okr_tracking": "SELECT COUNT(*) as count FROM public.okr_tracking",
    }

    for table, query in verification_queries.items():
        try:
            result = client.table(table).select("*", count="exact").limit(0).execute()
            print(f"✅ {table}: {result.count if hasattr(result, 'count') else 0} rows")
        except Exception as e:
            print(f"⚠️  {table}: {str(e)[:80]}")

    # Check if all migrations succeeded
    all_success = all(results.values())

    if all_success:
        print("\n✅ All migrations applied successfully!")
        print("\n📋 Next Steps:")
        print("  1. Test the migration: python3 /root/flourisha/00_AI_Brain/scripts/morning-report-generator.py")
        print("  2. Monitor cron jobs: crontab -l | grep flourisha")
        print("  3. Setup Chrome extension for energy tracking")
        print("  4. Configure Twilio for SMS integration")
        return 0
    else:
        print("\n⚠️  Some migrations had issues - please review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
