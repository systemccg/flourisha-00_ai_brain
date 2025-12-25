#!/usr/bin/env python3
"""
Autonomous Coding Agent (ClickUp Edition)
===============================================

A minimal harness demonstrating long-running autonomous coding with Claude.
This script implements the two-agent pattern (initializer + coding agent) and
incorporates all the strategies from the long-running agents guide.

Uses ClickUp for task management instead of Linear.

Example Usage:
    # Fresh start for Flourisha - delete old tasks, create from spec
    python run_autonomous_agent.py --project flourisha --fresh-start

    # Continue existing Flourisha project
    python run_autonomous_agent.py --project flourisha

    # Limit iterations for testing
    python run_autonomous_agent.py --project flourisha --max-iterations 5

    # Dry run - preview initialization without making changes
    python run_autonomous_agent.py --project flourisha --fresh-start --dry-run

    # Generic project (not Flourisha)
    python run_autonomous_agent.py --project-dir ./my_project
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_autonomous_agent
from prompts import set_active_project


# Configuration
# Using Claude Opus 4.5 as default for best coding and agentic performance
# See: https://www.anthropic.com/news/claude-opus-4-5
DEFAULT_MODEL = "claude-opus-4-5-20251101"

# Flourisha project directory
FLOURISHA_PROJECT_DIR = Path("/root/flourisha/00_AI_Brain/api")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent (ClickUp Edition) - Long-running agent harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fresh start for Flourisha - delete old tasks, create from spec
  python run_autonomous_agent.py --project flourisha --fresh-start

  # Continue existing Flourisha project
  python run_autonomous_agent.py --project flourisha

  # Limit iterations for testing
  python run_autonomous_agent.py --project flourisha --max-iterations 5

  # Dry run - preview initialization without making changes
  python run_autonomous_agent.py --project flourisha --fresh-start --dry-run

  # Generic project (not Flourisha)
  python run_autonomous_agent.py --project-dir ./my_project

Environment Variables:
  CLAUDE_CODE_OAUTH_TOKEN    Claude Code OAuth token (required)
  CLICKUP_API_KEY            ClickUp API key (required)
  CLICKUP_TEAM_ID            ClickUp team/workspace ID (required)
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Directory for the project (auto-set for --project flourisha)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project type for specialized prompts (e.g., 'flourisha'). Uses project-specific prompts and spec files.",
    )

    parser.add_argument(
        "--fresh-start",
        action="store_true",
        help="Delete all existing ClickUp tasks and recreate from AUTONOMOUS_TASK_SPEC.md. Required for first run of Flourisha project.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview fresh-start initialization without making changes.",
    )

    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only initialize ClickUp tasks, don't start the agent. Use with --fresh-start.",
    )

    return parser.parse_args()


def check_environment(dry_run: bool = False, init_only: bool = False) -> bool:
    """Check required environment variables.

    Args:
        dry_run: If True, only check ClickUp vars (not Claude token)
        init_only: If True, only check ClickUp vars for initialization
    """
    missing = []

    # Claude token only needed for actual agent runs
    if not dry_run and not init_only:
        if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
            missing.append("CLAUDE_CODE_OAUTH_TOKEN")

    if not os.environ.get("CLICKUP_API_KEY"):
        missing.append("CLICKUP_API_KEY")

    if not os.environ.get("CLICKUP_TEAM_ID"):
        missing.append("CLICKUP_TEAM_ID")

    if missing:
        print("Error: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet these before running:")
        if "CLAUDE_CODE_OAUTH_TOKEN" in missing:
            print("  export CLAUDE_CODE_OAUTH_TOKEN='your-token'")
        print("  export CLICKUP_API_KEY='pk_xxxxx'")
        print("  export CLICKUP_TEAM_ID='12345678'")
        return False

    return True


def initialize_flourisha(dry_run: bool = False) -> dict:
    """
    Initialize ClickUp for Flourisha project.

    Deletes all existing tasks and creates fresh ones from AUTONOMOUS_TASK_SPEC.md.

    Args:
        dry_run: If True, preview without making changes

    Returns:
        Initialization results dict
    """
    from clickup_init import initialize_clickup_for_flourisha, save_project_state

    print("\n" + "=" * 70)
    print("  FLOURISHA FRESH START")
    print("  Syncing ClickUp with AUTONOMOUS_TASK_SPEC.md")
    print("=" * 70 + "\n")

    if dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    results = initialize_clickup_for_flourisha(dry_run=dry_run)

    if not dry_run and results["created"] > 0:
        # Save project state for agent sessions
        FLOURISHA_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        save_project_state(
            project_dir=FLOURISHA_PROJECT_DIR,
            list_id="901112685055",
            meta_task_id=results["meta_task_id"],
            total_tasks=results["created"],
        )

    return results


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Check environment (dry-run and init-only only need ClickUp vars)
    if not check_environment(dry_run=args.dry_run, init_only=args.init_only):
        return

    # Handle Flourisha project specially
    if args.project == "flourisha":
        set_active_project("flourisha")
        project_dir = args.project_dir or FLOURISHA_PROJECT_DIR

        # Fresh start: initialize ClickUp from spec
        if args.fresh_start:
            results = initialize_flourisha(dry_run=args.dry_run)

            if args.dry_run:
                print("\nDry run complete. Run without --dry-run to apply changes.")
                return

            if results["created"] == 0:
                print("\nNo tasks created. Check AUTONOMOUS_TASK_SPEC.md and try again.")
                return

            print(f"\nClickUp initialized with {results['created']} tasks from spec.")

            if args.init_only:
                print("Initialization complete. Run without --init-only to start the agent.")
                return

            print("Starting autonomous agent...\n")

        else:
            # Check if project is initialized
            state_file = project_dir / ".clickup_project.json"
            if not state_file.exists():
                print("Error: Flourisha project not initialized.")
                print("\nRun with --fresh-start to initialize:")
                print("  python run_autonomous_agent.py --project flourisha --fresh-start")
                return

    elif args.project:
        # Other project types
        set_active_project(args.project)
        project_dir = args.project_dir or Path(f"./generations/{args.project}_project")

    else:
        # Default generic project
        project_dir = args.project_dir or Path("./generations/autonomous_demo_project")

    # Handle relative paths
    if not project_dir.is_absolute():
        if not str(project_dir).startswith("generations/"):
            project_dir = Path("generations") / project_dir

    # Run the agent
    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again (without --fresh-start)")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
