"""
Task Spec Parser
================

Parses AUTONOMOUS_TASK_SPEC.md to extract tasks for ClickUp import.
This makes the spec file the canonical source of truth for task definitions.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TaskSpec:
    """Parsed task specification."""
    id: str
    name: str
    priority: int  # 1=Urgent, 2=High, 3=Normal, 4=Low
    pillar: str  # CAPTURE, STORE, THINK, EXECUTE, GROW
    description: str
    category: str
    test_steps: list[str]
    acceptance_criteria: list[str]
    tags: list[str]


# Default spec file location
DEFAULT_SPEC_PATH = Path("/root/flourisha/00_AI_Brain/documentation/AUTONOMOUS_TASK_SPEC.md")

# Priority mapping
PRIORITY_MAP = {
    "1 (Urgent)": 1,
    "2 (High)": 2,
    "3 (Normal)": 3,
    "4 (Low)": 4,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
}

# Pillar mapping from section headers
PILLAR_MAP = {
    "PILLAR 1": "CAPTURE",
    "PILLAR 2": "STORE",
    "PILLAR 3": "THINK",
    "PILLAR 4": "EXECUTE",
    "PILLAR 5": "GROW",
}


def parse_task_spec(spec_path: Path = DEFAULT_SPEC_PATH) -> list[TaskSpec]:
    """
    Parse the AUTONOMOUS_TASK_SPEC.md file and extract all tasks.

    Args:
        spec_path: Path to the spec file

    Returns:
        List of TaskSpec objects
    """
    content = spec_path.read_text()
    tasks = []
    current_pillar = "UNKNOWN"

    # Split into sections by task headers
    # Pattern: ## Task X.X: Name
    task_pattern = re.compile(r'^## Task (\d+\.\d+): (.+)$', re.MULTILINE)
    pillar_pattern = re.compile(r'^# PILLAR (\d+): (\w+)', re.MULTILINE)

    # Find all pillar sections
    pillar_positions = []
    for match in pillar_pattern.finditer(content):
        pillar_num = match.group(1)
        pillar_name = match.group(2)
        pillar_positions.append((match.start(), f"PILLAR {pillar_num}", pillar_name))

    # Find all tasks
    for match in task_pattern.finditer(content):
        task_id = match.group(1)
        task_name = match.group(2)
        task_start = match.start()

        # Determine pillar based on position
        current_pillar = "UNKNOWN"
        for pos, pillar_key, pillar_name in pillar_positions:
            if pos < task_start:
                current_pillar = pillar_name

        # Find the end of this task (next ## or # header)
        next_header = re.search(r'^##? ', content[match.end():], re.MULTILINE)
        if next_header:
            task_end = match.end() + next_header.start()
        else:
            task_end = len(content)

        task_content = content[match.end():task_end]

        # Parse task components
        task = _parse_task_content(task_id, task_name, task_content, current_pillar)
        if task:
            tasks.append(task)

    return tasks


def _parse_task_content(task_id: str, task_name: str, content: str, pillar: str) -> Optional[TaskSpec]:
    """Parse the content of a single task section."""

    # Extract priority
    priority_match = re.search(r'\*\*Priority:\*\* (.+?)(?:\n|$)', content)
    priority_str = priority_match.group(1).strip() if priority_match else "3 (Normal)"
    priority = PRIORITY_MAP.get(priority_str, 3)

    # Extract pillar from task content (overrides parent pillar if found)
    pillar_match = re.search(r'\*\*Pillar:\*\* (.+?)(?:\n|$)', content)
    if pillar_match:
        pillar = pillar_match.group(1).strip()

    # Extract category
    category_match = re.search(r'### Category\n(.+?)(?:\n\n|\n###|$)', content, re.DOTALL)
    category = category_match.group(1).strip() if category_match else "functional"

    # Extract description (Feature Description section)
    desc_match = re.search(r'### Feature Description\n(.+?)(?:\n###|$)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract test steps
    test_match = re.search(r'### Test Steps\n(.+?)(?:\n###|$)', content, re.DOTALL)
    test_steps = []
    if test_match:
        for line in test_match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                test_steps.append(re.sub(r'^\d+\.\s*', '', line))

    # Extract acceptance criteria
    criteria_match = re.search(r'### Acceptance Criteria\n(.+?)(?:\n###|\n---|\n\n\n|$)', content, re.DOTALL)
    acceptance_criteria = []
    if criteria_match:
        for line in criteria_match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- [ ]'):
                acceptance_criteria.append(line[6:].strip())

    # Generate tags
    tags = [pillar.lower(), category.lower()]

    # Add priority tag
    if priority == 1:
        tags.append("urgent")
    elif priority == 2:
        tags.append("high-priority")

    return TaskSpec(
        id=task_id,
        name=task_name,
        priority=priority,
        pillar=pillar,
        description=description,
        category=category,
        test_steps=test_steps,
        acceptance_criteria=acceptance_criteria,
        tags=tags,
    )


def format_task_for_clickup(task: TaskSpec) -> dict:
    """
    Format a TaskSpec as a dict suitable for ClickUp task creation.

    Returns dict with keys: name, description, priority, tags
    """
    # Build description with all details
    description_parts = [
        f"**Task ID:** {task.id}",
        f"**Pillar:** {task.pillar}",
        f"**Category:** {task.category}",
        "",
        "## Description",
        task.description,
        "",
    ]

    if task.test_steps:
        description_parts.append("## Test Steps")
        for i, step in enumerate(task.test_steps, 1):
            description_parts.append(f"{i}. {step}")
        description_parts.append("")

    if task.acceptance_criteria:
        description_parts.append("## Acceptance Criteria")
        for criterion in task.acceptance_criteria:
            description_parts.append(f"- [ ] {criterion}")

    return {
        "name": f"[{task.id}] {task.name}",
        "description": "\n".join(description_parts),
        "priority": task.priority,
        "tags": task.tags,
    }


def get_tasks_summary(tasks: list[TaskSpec]) -> str:
    """Get a summary of parsed tasks."""
    by_pillar = {}
    by_priority = {1: 0, 2: 0, 3: 0, 4: 0}

    for task in tasks:
        by_pillar[task.pillar] = by_pillar.get(task.pillar, 0) + 1
        by_priority[task.priority] = by_priority.get(task.priority, 0) + 1

    lines = [
        f"Total tasks: {len(tasks)}",
        "",
        "By Pillar:",
    ]
    for pillar, count in sorted(by_pillar.items()):
        lines.append(f"  {pillar}: {count}")

    lines.extend([
        "",
        "By Priority:",
        f"  1 (Urgent): {by_priority[1]}",
        f"  2 (High): {by_priority[2]}",
        f"  3 (Normal): {by_priority[3]}",
        f"  4 (Low): {by_priority[4]}",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the parser
    tasks = parse_task_spec()
    print(get_tasks_summary(tasks))
    print("\nFirst 3 tasks:")
    for task in tasks[:3]:
        print(f"\n{task.id}: {task.name}")
        print(f"  Priority: {task.priority}, Pillar: {task.pillar}")
        print(f"  Criteria: {len(task.acceptance_criteria)}")
