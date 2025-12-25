"""
ClickUp Initialization
======================

Functions for initializing ClickUp with fresh tasks from AUTONOMOUS_TASK_SPEC.md.
This ensures ClickUp is a reflection of the spec, not a separate source of truth.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from task_spec_parser import parse_task_spec, format_task_for_clickup, get_tasks_summary


# ClickUp API configuration
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"

# Flourisha-specific configuration
FLOURISHA_SPACE_ID = "14700061"
FLOURISHA_LIST_ID = "901112685055"
FLOURISHA_LIST_NAME = "Flourisha API Backend"


def get_headers() -> dict:
    """Get ClickUp API headers."""
    api_key = os.environ.get("CLICKUP_API_KEY")
    if not api_key:
        raise ValueError("CLICKUP_API_KEY environment variable not set")
    return {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }


def get_all_tasks_in_list(list_id: str) -> list[dict]:
    """Get all tasks in a ClickUp list."""
    tasks = []
    page = 0

    while True:
        url = f"{CLICKUP_API_BASE}/list/{list_id}/task"
        params = {
            "page": page,
            "include_closed": "true",
            "subtasks": "true",
        }

        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()

        data = response.json()
        batch = data.get("tasks", [])

        if not batch:
            break

        tasks.extend(batch)
        page += 1

        # Safety limit
        if page > 20:
            break

    return tasks


def delete_all_tasks_in_list(list_id: str, dry_run: bool = False) -> int:
    """
    Delete all tasks in a ClickUp list.

    Args:
        list_id: ClickUp list ID
        dry_run: If True, only count tasks without deleting

    Returns:
        Number of tasks deleted (or would be deleted in dry_run)
    """
    print(f"Fetching tasks from list {list_id}...")
    tasks = get_all_tasks_in_list(list_id)

    if not tasks:
        print("No tasks found in list.")
        return 0

    print(f"Found {len(tasks)} tasks to delete.")

    if dry_run:
        print("DRY RUN - would delete these tasks:")
        for task in tasks[:10]:
            print(f"  - {task['name']}")
        if len(tasks) > 10:
            print(f"  ... and {len(tasks) - 10} more")
        return len(tasks)

    # Delete tasks in batches to avoid rate limits
    deleted = 0
    for task in tasks:
        task_id = task["id"]
        url = f"{CLICKUP_API_BASE}/task/{task_id}"

        try:
            response = requests.delete(url, headers=get_headers())
            response.raise_for_status()
            deleted += 1
            print(f"  Deleted: {task['name'][:50]}...")
        except requests.exceptions.RequestException as e:
            print(f"  Failed to delete {task['name']}: {e}")

        # Rate limiting - ClickUp allows 100 requests per minute
        time.sleep(0.7)

    print(f"Deleted {deleted} tasks.")
    return deleted


def create_tasks_from_spec(
    list_id: str,
    spec_path: Optional[Path] = None,
    dry_run: bool = False,
) -> tuple[int, str]:
    """
    Create ClickUp tasks from AUTONOMOUS_TASK_SPEC.md.

    Args:
        list_id: ClickUp list ID
        spec_path: Path to spec file (uses default if None)
        dry_run: If True, only parse and report without creating

    Returns:
        Tuple of (tasks_created, meta_task_id)
    """
    print("Parsing AUTONOMOUS_TASK_SPEC.md...")
    tasks = parse_task_spec(spec_path) if spec_path else parse_task_spec()

    print(get_tasks_summary(tasks))
    print()

    if dry_run:
        print("DRY RUN - would create these tasks:")
        for task in tasks[:5]:
            print(f"  [{task.id}] {task.name} (P{task.priority})")
        if len(tasks) > 5:
            print(f"  ... and {len(tasks) - 5} more")
        return len(tasks), ""

    # Create META task first
    print("\nCreating META task...")
    meta_task = create_meta_task(list_id, len(tasks))
    meta_task_id = meta_task.get("id", "")
    print(f"  META task created: {meta_task_id}")

    # Create tasks in batches
    print(f"\nCreating {len(tasks)} tasks...")
    created = 0

    for task_spec in tasks:
        task_data = format_task_for_clickup(task_spec)

        url = f"{CLICKUP_API_BASE}/list/{list_id}/task"
        payload = {
            "name": task_data["name"],
            "description": task_data["description"],
            "priority": task_data["priority"],
            "tags": task_data["tags"],
        }

        try:
            response = requests.post(url, headers=get_headers(), json=payload)
            response.raise_for_status()
            created += 1
            if created % 10 == 0:
                print(f"  Created {created}/{len(tasks)} tasks...")
        except requests.exceptions.RequestException as e:
            print(f"  Failed to create [{task_spec.id}] {task_spec.name}: {e}")

        # Rate limiting
        time.sleep(0.7)

    print(f"\nCreated {created} tasks.")
    return created, meta_task_id


def create_meta_task(list_id: str, total_tasks: int) -> dict:
    """Create the META progress tracker task."""
    description = f"""# Flourisha API Backend - Progress Tracker

**Initialized:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Pacific

## Project Overview

Building FastAPI backend that wraps existing Python services.

**Key Documents:**
- [AGENT_WORK_INDEX.md](/root/flourisha/00_AI_Brain/documentation/AGENT_WORK_INDEX.md) - Agent routing
- [SYSTEM_SPEC.md](/root/flourisha/00_AI_Brain/documentation/SYSTEM_SPEC.md) - Architecture
- [AUTONOMOUS_TASK_SPEC.md](/root/flourisha/00_AI_Brain/documentation/AUTONOMOUS_TASK_SPEC.md) - Task definitions

## Statistics

- Total Tasks: {total_tasks}
- Source: AUTONOMOUS_TASK_SPEC.md
- Status: Fresh initialization

## Session Log

### Session 0 - Initialization
- Deleted old tasks
- Created {total_tasks} tasks from spec
- Ready for autonomous development

---

*Add session summaries below this line*
"""

    url = f"{CLICKUP_API_BASE}/list/{list_id}/task"
    payload = {
        "name": "[META] Flourisha API Progress Tracker",
        "description": description,
        "priority": 1,  # Urgent - always at top
        "tags": ["meta", "tracking"],
    }

    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()
    return response.json()


def initialize_clickup_for_flourisha(
    list_id: str = FLOURISHA_LIST_ID,
    spec_path: Optional[Path] = None,
    dry_run: bool = False,
    skip_delete: bool = False,
) -> dict:
    """
    Full initialization: delete old tasks and create fresh from spec.

    Args:
        list_id: ClickUp list ID
        spec_path: Path to spec file
        dry_run: If True, only report without making changes
        skip_delete: If True, skip deletion (for empty list)

    Returns:
        Dict with initialization results
    """
    print("=" * 60)
    print("  CLICKUP INITIALIZATION FOR FLOURISHA")
    print("=" * 60)
    print()
    print(f"List ID: {list_id}")
    print(f"Dry Run: {dry_run}")
    print()

    results = {
        "deleted": 0,
        "created": 0,
        "meta_task_id": "",
        "timestamp": datetime.now().isoformat(),
    }

    # Step 1: Delete old tasks
    if not skip_delete:
        print("-" * 40)
        print("Step 1: Deleting existing tasks")
        print("-" * 40)
        results["deleted"] = delete_all_tasks_in_list(list_id, dry_run=dry_run)
        print()

    # Step 2: Create new tasks
    print("-" * 40)
    print("Step 2: Creating tasks from spec")
    print("-" * 40)
    results["created"], results["meta_task_id"] = create_tasks_from_spec(
        list_id, spec_path, dry_run=dry_run
    )

    print()
    print("=" * 60)
    print("  INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f"Deleted: {results['deleted']} tasks")
    print(f"Created: {results['created']} tasks")
    print(f"META Task ID: {results['meta_task_id']}")

    return results


def save_project_state(
    project_dir: Path,
    list_id: str,
    meta_task_id: str,
    total_tasks: int,
) -> None:
    """Save project state for agent sessions."""
    state = {
        "initialized": True,
        "created_at": datetime.now().isoformat(),
        "space_id": FLOURISHA_SPACE_ID,
        "list_id": list_id,
        "list_name": FLOURISHA_LIST_NAME,
        "meta_task_id": meta_task_id,
        "total_tasks": total_tasks,
        "routing_doc": "/root/flourisha/00_AI_Brain/documentation/AGENT_WORK_INDEX.md",
        "spec_doc": "/root/flourisha/00_AI_Brain/documentation/AUTONOMOUS_TASK_SPEC.md",
        "project_root": "/root/flourisha/00_AI_Brain/api",
        "docs_root": "/root/flourisha/00_AI_Brain/documentation",
    }

    state_file = project_dir / ".clickup_project.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Saved project state to {state_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize ClickUp for Flourisha")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--skip-delete", action="store_true", help="Skip deletion step")
    parser.add_argument("--list-id", default=FLOURISHA_LIST_ID, help="ClickUp list ID")

    args = parser.parse_args()

    results = initialize_clickup_for_flourisha(
        list_id=args.list_id,
        dry_run=args.dry_run,
        skip_delete=args.skip_delete,
    )
