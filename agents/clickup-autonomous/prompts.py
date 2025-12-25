"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
Supports project-specific prompts (e.g., flourisha_initializer.md).
"""

import shutil
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"

# Set this to use project-specific prompts
# Options: None (default), "flourisha"
ACTIVE_PROJECT = None


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory.

    Checks for project-specific prompts first (e.g., flourisha_initializer.md),
    then falls back to default prompts.
    """
    # Check for project-specific prompt
    if ACTIVE_PROJECT:
        project_prompt = PROMPTS_DIR / f"{ACTIVE_PROJECT}_{name}.md"
        if project_prompt.exists():
            print(f"Using project-specific prompt: {project_prompt.name}")
            return project_prompt.read_text()

    # Fall back to default
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def set_active_project(project: str) -> None:
    """Set the active project for prompt selection."""
    global ACTIVE_PROJECT
    ACTIVE_PROJECT = project
    print(f"Active project set to: {project}")


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt")


def get_coding_prompt() -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding_prompt")


def copy_spec_to_project(project_dir: Path) -> None:
    """Copy the app spec file into the project directory for the agent to read.

    Uses project-specific spec if available.
    """
    # Check for project-specific spec
    if ACTIVE_PROJECT:
        project_spec = PROMPTS_DIR / f"{ACTIVE_PROJECT}_spec.txt"
        if project_spec.exists():
            spec_source = project_spec
            print(f"Using project-specific spec: {project_spec.name}")
        else:
            spec_source = PROMPTS_DIR / "app_spec.txt"
    else:
        spec_source = PROMPTS_DIR / "app_spec.txt"

    spec_dest = project_dir / "app_spec.txt"
    if not spec_dest.exists():
        shutil.copy(spec_source, spec_dest)
        print(f"Copied {spec_source.name} to project directory")
