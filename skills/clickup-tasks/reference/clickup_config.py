"""
ClickUp Configuration
=====================

Configuration constants for ClickUp integration.
These values are used in prompts and for project state management.

IMPORTANT: When creating tasks via API, use 'markdown_description' field
instead of 'description' for proper rich text formatting in ClickUp UI.
"""

import os

# Environment variables (must be set before running)
CLICKUP_API_KEY = os.environ.get("CLICKUP_API_KEY")
CLICKUP_TEAM_ID = os.environ.get("CLICKUP_TEAM_ID")

# Default number of tasks to create (can be overridden via command line)
DEFAULT_TASK_COUNT = 50

# Task status workflow (Project Central custom statuses)
# Your workspace uses these statuses:
STATUS_OPEN = "--"              # Default open status (type: open)
STATUS_IN_PROGRESS = "in progress"  # Working on it (type: custom)
STATUS_WAITING = "waiting for"  # Blocked/waiting (type: custom)
STATUS_ON_HOLD = "on hold"      # Paused (type: custom)
STATUS_IN_REVIEW = "in review"  # Ready for review (type: done)
STATUS_DONE = "done"            # Completed (type: done)
STATUS_CLOSED = "Closed"        # Archived (type: closed)

# Simplified mapping for autonomous coding
STATUS_TODO = "--"              # Use "--" as the "to do" equivalent
STATUS_COMPLETE = "done"        # Use "done" as complete

# Category tags (created in Project Central space)
TAG_FUNCTIONAL = "functional"       # Green #4CAF50 - Feature implementation
TAG_INFRASTRUCTURE = "infrastructure"  # Blue #2196F3 - Setup, config, tooling
TAG_STYLE = "style"                 # Purple #9C27B0 - UI/UX, visual changes

# Priority mapping (ClickUp uses 1-4 where 1=Urgent, 4=Low)
PRIORITY_URGENT = 1
PRIORITY_HIGH = 2
PRIORITY_NORMAL = 3
PRIORITY_LOW = 4

# User IDs for assignment
USER_GREG_WASMUTH = 12782467      # For tasks needing human review
USER_FLOURISHA = 87375090          # system@cocreatorsgroup.com - AI agent tasks

# ClickUp List IDs (Flourisha folder)
LIST_AI_BRAIN_DEVELOPMENT = "901112608092"  # AI infrastructure tasks
LIST_IDEA_SCRATCHPAD = "901112609506"       # Ideas, YouTube links, pre-project concepts

# Folder and Space IDs
FOLDER_FLOURISHA = "90117368142"
SPACE_PROJECT_CENTRAL = "14700061"

# Centralized paths (source of truth in AI Brain, symlinked from ~/.claude)
PATH_AI_BRAIN = "/root/flourisha/00_AI_Brain"
PATH_SCRATCHPAD = "/root/flourisha/00_AI_Brain/scratchpad"  # symlink: ~/.claude/scratchpad
PATH_PLANS = "/root/flourisha/00_AI_Brain/plans"            # symlink: ~/.claude/plans
PATH_PROJECTS = "/root/flourisha/01f_Flourisha_Projects"

# Directory-to-List mapping
DIRECTORY_LIST_MAP = {
    PATH_SCRATCHPAD: LIST_IDEA_SCRATCHPAD,
    "/root/.claude/scratchpad": LIST_IDEA_SCRATCHPAD,  # symlink compatibility
    PATH_AI_BRAIN: LIST_AI_BRAIN_DEVELOPMENT,
    # Formal projects in 01f_Flourisha_Projects get their own lists (created on demand)
}

# Local marker file to track ClickUp project initialization
CLICKUP_PROJECT_MARKER = ".clickup_project.json"

# Meta task title for project tracking and session handoff
META_TASK_TITLE = "[META] Project Progress Tracker"
