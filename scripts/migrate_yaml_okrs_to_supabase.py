#!/usr/bin/env python3
"""
Migrate Q1_2026.yaml OKRs to Supabase

This script reads the Q1_2026.yaml file and inserts the OKRs into Supabase
as personal OKRs for the default user (Greg).

Usage:
    python3 migrate_yaml_okrs_to_supabase.py [--dry-run] [--user-id UUID]

Options:
    --dry-run   Show what would be inserted without actually inserting
    --user-id   Override the default user ID
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('/root/.claude/.env')

# Configuration
OKR_YAML_PATH = Path('/root/flourisha/00_AI_Brain/okr/Q1_2026.yaml')
DEFAULT_TENANT_ID = 'greg_personal'  # Default tenant for personal OKRs


def load_yaml_okrs(yaml_path: Path) -> Dict[str, Any]:
    """Load OKRs from YAML file"""
    if not yaml_path.exists():
        raise FileNotFoundError(f"OKR file not found: {yaml_path}")

    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def transform_to_supabase_records(
    yaml_data: Dict[str, Any],
    user_id: Optional[str] = None,
    tenant_id: str = DEFAULT_TENANT_ID
) -> List[Dict[str, Any]]:
    """
    Transform YAML OKR data to Supabase records

    Each key result becomes a separate row in okr_tracking
    (this matches the existing schema structure)
    """
    records = []
    quarter = yaml_data.get('quarter', 'Q1_2026')

    for objective in yaml_data.get('objectives', []):
        obj_id = objective['id']
        obj_title = objective['title']
        obj_description = objective.get('description', '')
        owner = objective.get('owner', '')
        department = objective.get('department', '')
        target_date = objective.get('target_completion', None)

        # Convert target_completion to date if it's a string
        if isinstance(target_date, str):
            try:
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            except ValueError:
                target_date = None

        for kr in objective.get('key_results', []):
            record = {
                'id': str(uuid4()),  # Generate new UUID for each record
                'tenant_id': tenant_id,
                'quarter': quarter,
                'objective_id': obj_id,
                'objective_title': obj_title,
                'objective_description': obj_description,
                'owner': owner,
                'target_completion_date': str(target_date) if target_date else None,
                'key_result_id': kr['id'],
                'key_result_title': kr['title'],
                'key_result_target': float(kr['target']),
                'key_result_current': float(kr.get('current', 0)),
                'key_result_unit': kr.get('unit', 'count'),
                'status': 'not_started',  # Default status
            }

            # Store department in metadata dict for display (not a DB column yet)
            # This will be stripped before insert
            record['_metadata'] = {'department': department}

            records.append(record)

    return records


def insert_to_supabase(
    client: Client,
    records: List[Dict[str, Any]],
    dry_run: bool = False
) -> Dict[str, Any]:
    """Insert OKR records to Supabase"""
    results = {
        'total': len(records),
        'inserted': 0,
        'errors': []
    }

    if dry_run:
        print("\n🔍 DRY RUN - No data will be inserted\n")
        for record in records:
            print(f"  Would insert: {record['objective_id']} / {record['key_result_id']}")
            print(f"    Title: {record['key_result_title']}")
            print(f"    Target: {record['key_result_target']} {record['key_result_unit']}")
            dept = record.get('_metadata', {}).get('department', 'N/A')
            print(f"    Department: {dept}")
            print()
        return results

    # Strip metadata fields before insert (they're not DB columns)
    clean_records = []
    for r in records:
        clean = {k: v for k, v in r.items() if not k.startswith('_')}
        clean_records.append(clean)
    records = clean_records

    # Check if records already exist
    existing = client.table('okr_tracking').select('objective_id, key_result_id').eq(
        'tenant_id', records[0]['tenant_id']
    ).eq('quarter', records[0]['quarter']).execute()

    existing_keys = {(r['objective_id'], r['key_result_id']) for r in existing.data}

    # Filter out already existing records
    new_records = [
        r for r in records
        if (r['objective_id'], r['key_result_id']) not in existing_keys
    ]

    if not new_records:
        print("✅ All OKRs already exist in Supabase - nothing to insert")
        return results

    print(f"📥 Inserting {len(new_records)} new OKRs (skipping {len(records) - len(new_records)} existing)...")

    # Insert in batches of 50
    batch_size = 50
    for i in range(0, len(new_records), batch_size):
        batch = new_records[i:i + batch_size]
        try:
            result = client.table('okr_tracking').insert(batch).execute()
            results['inserted'] += len(result.data)
            print(f"  ✓ Inserted batch {i // batch_size + 1}: {len(result.data)} records")
        except Exception as e:
            error_msg = f"Batch {i // batch_size + 1}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"  ✗ Error in batch {i // batch_size + 1}: {e}")

    return results


def create_default_tags(
    client: Client,
    tenant_id: str,
    user_id: Optional[str] = None,
    dry_run: bool = False
) -> None:
    """Create default tags for organizing OKRs"""
    default_tags = [
        {'name': 'high-priority', 'color': '#EF4444', 'description': 'High priority items'},
        {'name': 'strategic', 'color': '#8B5CF6', 'description': 'Strategic initiatives'},
        {'name': 'operational', 'color': '#3B82F6', 'description': 'Day-to-day operations'},
        {'name': 'learning', 'color': '#10B981', 'description': 'Learning and growth'},
        {'name': 'health', 'color': '#F59E0B', 'description': 'Health and wellness'},
        {'name': 'blocked', 'color': '#DC2626', 'description': 'Blocked items needing attention'},
    ]

    if dry_run:
        print("\n🏷️ Would create default tags:")
        for tag in default_tags:
            print(f"  - {tag['name']} ({tag['color']})")
        return

    print("\n🏷️ Creating default tags...")

    for tag in default_tags:
        try:
            record = {
                'name': tag['name'],
                'color': tag['color'],
                'description': tag['description'],
                'tenant_id': tenant_id,
            }
            if user_id:
                record['user_id'] = user_id

            # Check if tag exists
            existing = client.table('okr_tags').select('id').eq(
                'name', tag['name']
            ).eq('tenant_id', tenant_id).execute()

            if not existing.data:
                client.table('okr_tags').insert(record).execute()
                print(f"  ✓ Created tag: {tag['name']}")
            else:
                print(f"  - Tag exists: {tag['name']}")

        except Exception as e:
            print(f"  ✗ Error creating tag {tag['name']}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Migrate YAML OKRs to Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--user-id', type=str, help='User ID for personal OKRs')
    parser.add_argument('--tenant-id', type=str, default=DEFAULT_TENANT_ID, help='Tenant ID')
    args = parser.parse_args()

    print("=" * 60)
    print("OKR Migration: YAML → Supabase")
    print("=" * 60)

    # Initialize Supabase client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    client = create_client(url, key)
    print(f"✅ Connected to Supabase: {url[:50]}...")

    # Load YAML data
    print(f"\n📄 Loading OKRs from: {OKR_YAML_PATH}")
    yaml_data = load_yaml_okrs(OKR_YAML_PATH)

    quarter = yaml_data.get('quarter', 'Q1_2026')
    objectives = yaml_data.get('objectives', [])
    total_krs = sum(len(obj.get('key_results', [])) for obj in objectives)

    print(f"   Quarter: {quarter}")
    print(f"   Objectives: {len(objectives)}")
    print(f"   Key Results: {total_krs}")

    # Transform to Supabase records
    print(f"\n🔄 Transforming to Supabase format...")
    records = transform_to_supabase_records(
        yaml_data,
        user_id=args.user_id,
        tenant_id=args.tenant_id
    )
    print(f"   Generated {len(records)} records")

    # Insert to Supabase
    results = insert_to_supabase(client, records, dry_run=args.dry_run)

    # Create default tags
    create_default_tags(client, args.tenant_id, args.user_id, dry_run=args.dry_run)

    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"  Total records: {results['total']}")
    print(f"  Inserted: {results['inserted']}")
    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")
        for err in results['errors']:
            print(f"    - {err}")

    if args.dry_run:
        print("\n💡 Run without --dry-run to actually insert the data")

    print("\n✅ Migration complete!")


if __name__ == '__main__':
    main()
