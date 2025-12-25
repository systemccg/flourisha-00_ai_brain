"""
ClickUp Configuration
=====================

Configuration constants for ClickUp integration.
These values are used in prompts and for project state management.
"""

import os

# Environment variables (must be set before running)
CLICKUP_API_KEY = os.environ.get("CLICKUP_API_KEY")
CLICKUP_TEAM_ID = os.environ.get("CLICKUP_TEAM_ID")

# Default number of tasks to create (can be overridden via command line)
DEFAULT_TASK_COUNT = 50

# Task status workflow (ClickUp default states - customize per workspace)
STATUS_TODO = "to do"
STATUS_IN_PROGRESS = "in progress"
STATUS_DONE = "complete"

# Tag categories (map to feature types)
TAG_FUNCTIONAL = "functional"
TAG_STYLE = "style"
TAG_INFRASTRUCTURE = "infrastructure"

# Priority mapping (ClickUp uses 1-4 where 1=Urgent, 4=Low)
PRIORITY_URGENT = 1
PRIORITY_HIGH = 2
PRIORITY_NORMAL = 3
PRIORITY_LOW = 4

# Local marker file to track ClickUp project initialization
CLICKUP_PROJECT_MARKER = ".clickup_project.json"

# Meta task title for project tracking and session handoff
META_TASK_TITLE = "[META] Project Progress Tracker"
