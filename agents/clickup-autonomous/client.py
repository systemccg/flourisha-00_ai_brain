"""
Claude SDK Client Configuration
===============================

Functions for creating and configuring the Claude Agent SDK client.
"""

import json
import os
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from security import bash_security_hook


# Puppeteer MCP tools for browser automation
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_select",
    "mcp__puppeteer__puppeteer_hover",
    "mcp__puppeteer__puppeteer_evaluate",
]

# ClickUp MCP tools for project management
# Using @taazkareem/clickup-mcp-server
CLICKUP_TOOLS = [
    # Workspace navigation
    "mcp__clickup__get_workspace_hierarchy",
    "mcp__clickup__get_workspace_members",
    "mcp__clickup__find_member_by_name",
    "mcp__clickup__resolve_assignees",
    # Task management
    "mcp__clickup__create_task",
    "mcp__clickup__create_bulk_tasks",
    "mcp__clickup__get_task",
    "mcp__clickup__get_tasks",
    "mcp__clickup__get_workspace_tasks",
    "mcp__clickup__update_task",
    "mcp__clickup__update_bulk_tasks",
    "mcp__clickup__delete_task",
    "mcp__clickup__delete_bulk_tasks",
    "mcp__clickup__move_task",
    "mcp__clickup__move_bulk_tasks",
    "mcp__clickup__duplicate_task",
    # Comments
    "mcp__clickup__get_task_comments",
    "mcp__clickup__create_task_comment",
    "mcp__clickup__attach_task_file",
    # Lists and Folders
    "mcp__clickup__create_list",
    "mcp__clickup__get_list",
    "mcp__clickup__update_list",
    "mcp__clickup__delete_list",
    "mcp__clickup__create_folder",
    "mcp__clickup__get_folder",
    "mcp__clickup__update_folder",
    "mcp__clickup__delete_folder",
    "mcp__clickup__create_list_in_folder",
    # Tags
    "mcp__clickup__get_space_tags",
    "mcp__clickup__create_space_tag",
    "mcp__clickup__update_space_tag",
    "mcp__clickup__delete_space_tag",
    "mcp__clickup__add_tag_to_task",
    "mcp__clickup__remove_tag_from_task",
    # Time tracking
    "mcp__clickup__get_task_time_entries",
    "mcp__clickup__start_time_tracking",
    "mcp__clickup__stop_time_tracking",
    "mcp__clickup__add_time_entry",
    "mcp__clickup__delete_time_entry",
    "mcp__clickup__get_current_time_entry",
    # Documents
    "mcp__clickup__create_document",
    "mcp__clickup__get_document",
    "mcp__clickup__list_documents",
    "mcp__clickup__list_document_pages",
    "mcp__clickup__get_document_pages",
    "mcp__clickup__create_document_pages",
    "mcp__clickup__update_document_page",
]

# Built-in tools
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(project_dir: Path, model: str) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client with multi-layered security.

    Args:
        project_dir: Directory for the project
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient

    Security layers (defense in depth):
    1. Sandbox - OS-level bash command isolation prevents filesystem escape
    2. Permissions - File operations restricted to project_dir only
    3. Security hooks - Bash commands validated against an allowlist
       (see security.py for ALLOWED_COMMANDS)
    """
    api_key = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not api_key:
        raise ValueError(
            "CLAUDE_CODE_OAUTH_TOKEN environment variable not set.\n"
            "Run 'claude setup-token' after installing the Claude Code CLI."
        )

    clickup_api_key = os.environ.get("CLICKUP_API_KEY")
    if not clickup_api_key:
        raise ValueError(
            "CLICKUP_API_KEY environment variable not set.\n"
            "Get your API key from: https://app.clickup.com/settings/apps"
        )

    clickup_team_id = os.environ.get("CLICKUP_TEAM_ID")
    if not clickup_team_id:
        raise ValueError(
            "CLICKUP_TEAM_ID environment variable not set.\n"
            "Find your team ID in your ClickUp workspace URL."
        )

    # Create comprehensive security settings
    # Note: Using relative paths ("./**") restricts access to project directory
    # since cwd is set to project_dir
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",  # Auto-approve edits within allowed directories
            "allow": [
                # Allow all file operations within the project directory
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                # Bash permission granted here, but actual commands are validated
                # by the bash_security_hook (see security.py for allowed commands)
                "Bash(*)",
                # Allow Puppeteer MCP tools for browser automation
                *PUPPETEER_TOOLS,
                # Allow ClickUp MCP tools for project management
                *CLICKUP_TOOLS,
            ],
        },
    }

    # Ensure project directory exists before creating settings file
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to a file in the project directory
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    print(f"Created security settings at {settings_file}")
    print("   - Sandbox enabled (OS-level bash isolation)")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist (see security.py)")
    print("   - MCP servers: puppeteer (browser automation), clickup (project management)")
    print()

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt="You are an expert full-stack developer building a production-quality web application. You use ClickUp for project management and tracking all your work.",
            allowed_tools=[
                *BUILTIN_TOOLS,
                *PUPPETEER_TOOLS,
                *CLICKUP_TOOLS,
            ],
            mcp_servers={
                "puppeteer": {"command": "npx", "args": ["puppeteer-mcp-server"]},
                # ClickUp MCP using @taazkareem/clickup-mcp-server
                # Runs via npx with stdio transport
                "clickup": {
                    "command": "npx",
                    "args": ["-y", "@taazkareem/clickup-mcp-server@latest"],
                    "env": {
                        "CLICKUP_API_KEY": clickup_api_key,
                        "CLICKUP_TEAM_ID": clickup_team_id,
                    }
                }
            },
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),  # Use absolute path
        )
    )
