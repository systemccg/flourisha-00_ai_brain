#!/usr/bin/env python3
"""
Fetch testable features from ClickUp Flourisha Frontend Dashboard.

This script queries ClickUp to get all COMPLETED features that should be testable.
Used by the frontend-tester agent to understand what features exist and should work.

Usage:
    python3 get_testable_features.py              # JSON output
    python3 get_testable_features.py --format=md  # Markdown output
    python3 get_testable_features.py --summary    # Just counts
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

# ClickUp Configuration
FRONTEND_DASHBOARD_LIST_ID = "901112777033"
ENV_FILE = Path("/root/flourisha/00_AI_Brain/.env")


def get_api_key() -> str:
    """Load ClickUp API key from environment."""
    if key := os.environ.get("CLICKUP_API_KEY"):
        return key

    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        for line in content.split('\n'):
            if line.startswith('CLICKUP_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"\'')

    raise ValueError("CLICKUP_API_KEY not found in environment or .env file")


def fetch_tasks(api_key: str, list_id: str) -> list[dict]:
    """Fetch all tasks from a ClickUp list."""
    headers = {"Authorization": api_key}

    resp = httpx.get(
        f"https://api.clickup.com/api/v2/list/{list_id}/task",
        headers=headers,
        params={"include_closed": "true", "subtasks": "true"}
    )
    resp.raise_for_status()
    return resp.json().get("tasks", [])


def categorize_tasks(tasks: list[dict]) -> dict:
    """Categorize tasks by status and phase."""
    result = {
        "completed": [],
        "in_progress": [],
        "pending": [],
        "by_phase": {
            "P1": [],  # Core setup (1-15)
            "P2": [],  # Search, PARA, Graph (16-30)
            "P3": [],  # OKRs, Energy (31-43)
            "P4": [],  # Settings, Integrations (44-60)
        }
    }

    for task in tasks:
        status = task.get("status", {}).get("status", "").lower()
        name = task.get("name", "Unnamed")
        task_id = task.get("id", "")

        task_info = {
            "id": task_id,
            "name": name,
            "status": status,
            "url": f"https://app.clickup.com/t/{task_id}"
        }

        # Categorize by status
        if status == "done":
            result["completed"].append(task_info)
        elif status == "in progress":
            result["in_progress"].append(task_info)
        else:
            result["pending"].append(task_info)

        # Categorize by phase (extract from task name like [P1-01])
        if "[P1-" in name:
            result["by_phase"]["P1"].append(task_info)
        elif "[P2-" in name:
            result["by_phase"]["P2"].append(task_info)
        elif "[P3-" in name:
            result["by_phase"]["P3"].append(task_info)
        elif "[P4-" in name:
            result["by_phase"]["P4"].append(task_info)

    return result


def format_json(data: dict) -> str:
    """Format output as JSON."""
    output = {
        "list_id": FRONTEND_DASHBOARD_LIST_ID,
        "list_name": "Flourisha Frontend Dashboard",
        "summary": {
            "total": len(data["completed"]) + len(data["in_progress"]) + len(data["pending"]),
            "completed": len(data["completed"]),
            "in_progress": len(data["in_progress"]),
            "pending": len(data["pending"]),
        },
        "phases": {
            phase: len(tasks) for phase, tasks in data["by_phase"].items()
        },
        "completed_features": data["completed"],
        "in_progress_features": data["in_progress"],
    }
    return json.dumps(output, indent=2)


def format_markdown(data: dict) -> str:
    """Format output as Markdown."""
    lines = [
        "# Flourisha Frontend Dashboard - Testable Features",
        "",
        f"**List ID:** {FRONTEND_DASHBOARD_LIST_ID}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Completed | {len(data['completed'])} |",
        f"| In Progress | {len(data['in_progress'])} |",
        f"| Pending | {len(data['pending'])} |",
        f"| **Total** | {len(data['completed']) + len(data['in_progress']) + len(data['pending'])} |",
        "",
        "## Completed Features (Should Be Testable)",
        "",
    ]

    for task in sorted(data["completed"], key=lambda x: x["name"]):
        lines.append(f"- ✅ {task['name']}")

    if data["in_progress"]:
        lines.append("")
        lines.append("## In Progress (May Be Partially Testable)")
        lines.append("")
        for task in data["in_progress"]:
            lines.append(f"- 🔄 {task['name']}")

    lines.append("")
    lines.append("## Phase Breakdown")
    lines.append("")
    lines.append("| Phase | Description | Tasks |")
    lines.append("|-------|-------------|-------|")

    phase_desc = {
        "P1": "Core setup, auth, layout",
        "P2": "Search, PARA, Graph, Uploads",
        "P3": "OKRs, Energy tracking",
        "P4": "Settings, Integrations",
    }

    for phase, tasks in data["by_phase"].items():
        completed = sum(1 for t in tasks if t["status"] == "done")
        lines.append(f"| {phase} | {phase_desc.get(phase, '')} | {completed}/{len(tasks)} |")

    return "\n".join(lines)


def format_summary(data: dict) -> str:
    """Format output as brief summary."""
    total = len(data["completed"]) + len(data["in_progress"]) + len(data["pending"])
    return f"""Flourisha Frontend Dashboard Status:
  Completed: {len(data['completed'])}/{total} features
  In Progress: {len(data['in_progress'])}
  Pending: {len(data['pending'])}

Phase Coverage:
  P1 (Core): {sum(1 for t in data['by_phase']['P1'] if t['status'] == 'done')}/{len(data['by_phase']['P1'])}
  P2 (Search/Graph): {sum(1 for t in data['by_phase']['P2'] if t['status'] == 'done')}/{len(data['by_phase']['P2'])}
  P3 (OKRs/Energy): {sum(1 for t in data['by_phase']['P3'] if t['status'] == 'done')}/{len(data['by_phase']['P3'])}
  P4 (Settings): {sum(1 for t in data['by_phase']['P4'] if t['status'] == 'done')}/{len(data['by_phase']['P4'])}
"""


def main():
    parser = argparse.ArgumentParser(description="Fetch testable features from ClickUp")
    parser.add_argument("--format", choices=["json", "md", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--summary", action="store_true",
                        help="Show brief summary only")
    args = parser.parse_args()

    try:
        api_key = get_api_key()
        tasks = fetch_tasks(api_key, FRONTEND_DASHBOARD_LIST_ID)
        data = categorize_tasks(tasks)

        if args.summary:
            print(format_summary(data))
        elif args.format in ("md", "markdown"):
            print(format_markdown(data))
        else:
            print(format_json(data))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
