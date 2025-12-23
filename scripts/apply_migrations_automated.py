#!/usr/bin/env python3
"""
Automated Supabase Migration Applier
Provides multiple methods to apply migrations based on available tools
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def load_env():
    """Load environment variables"""
    env_file = Path.home() / ".claude" / ".env"
    if not env_file.exists():
        print("❌ ERROR: ~/.claude/.env not found")
        sys.exit(1)
    
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    return env_vars

def read_migration(migration_path):
    """Read SQL migration file"""
    try:
        with open(migration_path) as f:
            return f.read()
    except FileNotFoundError:
        return None

def method_1_supabase_cli():
    """Method 1: Use Supabase CLI (requires installation)"""
    print("\n" + "="*60)
    print("Method 1: Supabase CLI")
    print("="*60)
    
    result = subprocess.run(["which", "supabase"], capture_output=True)
    if result.returncode == 0:
        print("✅ Supabase CLI found")
        print("\nRunning: supabase db push")
        result = subprocess.run(
            ["supabase", "db", "push"],
            cwd="/root/flourisha/00_AI_Brain"
        )
        return result.returncode == 0
    else:
        print("⚠️  Supabase CLI not installed")
        print("\nInstall with: bun install -g supabase")
        return False

def method_2_manual_dashboard():
    """Method 2: Manual Dashboard (requires user action)"""
    print("\n" + "="*60)
    print("Method 2: Supabase Dashboard (Manual)")
    print("="*60)
    
    migrations = [
        ("/root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql", "Energy Tracking"),
        ("/root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql", "OKR Tracking"),
    ]
    
    print("\n📋 Manual Migration Steps:\n")
    
    for i, (path, name) in enumerate(migrations, 1):
        sql_content = read_migration(path)
        if sql_content:
            print(f"{i}. {name} Migration")
            print(f"   File: {path}")
            print(f"   Size: {len(sql_content)} bytes")
            print(f"   Steps:")
            print(f"     - Go to https://app.supabase.com")
            print(f"     - Open SQL Editor")
            print(f"     - Click 'New Query'")
            print(f"     - Copy content from {Path(path).name}")
            print(f"     - Click 'Run'")
            print()
    
    print("⚠️  Requires manual dashboard access")
    return False

def method_3_generate_script():
    """Method 3: Generate migration script for manual execution"""
    print("\n" + "="*60)
    print("Method 3: Generated Migration Script")
    print("="*60)
    
    migrations_dir = Path("/root/flourisha/00_AI_Brain/database/migrations")
    script_path = Path("/tmp/flourisha_migrations.sql")
    
    print(f"\n📝 Generating combined migration script: {script_path}")
    
    with open(script_path, 'w') as out:
        out.write("-- Flourisha AI Brain - Combined Migrations\n")
        out.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
        
        for migration_file in sorted(migrations_dir.glob("*.sql")):
            sql_content = read_migration(migration_file)
            if sql_content:
                out.write(f"-- ============================================\n")
                out.write(f"-- Migration: {migration_file.name}\n")
                out.write(f"-- ============================================\n\n")
                out.write(sql_content)
                out.write("\n\n")
        
        out.write("-- All migrations completed\n")
    
    print(f"✅ Generated: {script_path}")
    print(f"\nUsage:")
    print(f"  # In psql:")
    print(f"  \\i {script_path}")
    print(f"\n  # Via curl (if custom RPC exists):")
    print(f"  cat {script_path} | curl -X POST https://db.leadingai.info/rest/v1/rpc/execute_sql \\\\")
    print(f"    -H 'Authorization: Bearer SERVICE_KEY' \\\\")
    print(f"    -d '{{\"sql\":\"...\"}}' ")
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 Flourisha AI Brain - Migration Applier")
    print("="*60)
    
    # Load environment
    print("\n🔧 Loading configuration...")
    env_vars = load_env()
    
    supabase_url = env_vars.get("SUPABASE_URL")
    print(f"✅ SUPABASE_URL: {supabase_url}")
    
    # Check migration files
    print("\n📁 Checking migration files...")
    migrations_dir = Path("/root/flourisha/00_AI_Brain/database/migrations")
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    migration_files = sorted(migrations_dir.glob("*.sql"))
    print(f"✅ Found {len(migration_files)} migration file(s):")
    for f in migration_files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    
    # Try methods in order
    print("\n" + "="*60)
    print("🔍 Attempting migration methods...")
    print("="*60)
    
    # Try CLI first
    if method_1_supabase_cli():
        print("\n✅ SUCCESS: Migrations applied via Supabase CLI")
        return 0
    
    # Fall back to manual + script generation
    method_2_manual_dashboard()
    method_3_generate_script()
    
    print("\n" + "="*60)
    print("📊 Migration Status: PENDING MANUAL ACTION")
    print("="*60)
    print("\n⚠️  Next steps:")
    print("  1. Install Supabase CLI: bun install -g supabase")
    print("  2. Run: supabase db push")
    print("  OR")
    print("  3. Use Supabase Dashboard: https://app.supabase.com")
    print("  OR")
    print("  4. Execute generated script: psql -f /tmp/flourisha_migrations.sql")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

