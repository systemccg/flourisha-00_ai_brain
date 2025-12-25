"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Progress is tracked via ClickUp tasks, with local state cached in .clickup_project.json.
"""

import json
from pathlib import Path

from clickup_config import CLICKUP_PROJECT_MARKER


def load_clickup_project_state(project_dir: Path) -> dict | None:
    """
    Load the ClickUp project state from the marker file.

    Args:
        project_dir: Directory containing .clickup_project.json

    Returns:
        Project state dict or None if not initialized
    """
    marker_file = project_dir / CLICKUP_PROJECT_MARKER

    if not marker_file.exists():
        return None

    try:
        with open(marker_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def is_clickup_initialized(project_dir: Path) -> bool:
    """
    Check if ClickUp project has been initialized.

    Args:
        project_dir: Directory to check

    Returns:
        True if .clickup_project.json exists and is valid
    """
    state = load_clickup_project_state(project_dir)
    return state is not None and state.get("initialized", False)


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """
    Print a summary of current progress.

    Since actual progress is tracked in ClickUp, this reads the local
    state file for cached information. The agent updates ClickUp directly
    and reports progress in session comments.
    """
    state = load_clickup_project_state(project_dir)

    if state is None:
        print("\nProgress: ClickUp project not yet initialized")
        return

    total = state.get("total_tasks", 0)
    meta_task = state.get("meta_task_id", "unknown")
    list_name = state.get("list_name", "unknown")

    print(f"\nClickUp Project Status:")
    print(f"  List: {list_name}")
    print(f"  Total tasks created: {total}")
    print(f"  META task ID: {meta_task}")
    print(f"  (Check ClickUp for current Complete/In Progress/To Do counts)")
