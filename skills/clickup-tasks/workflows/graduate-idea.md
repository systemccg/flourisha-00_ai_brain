# Graduate Idea to Project Workflow

Convert a validated idea from Idea Scratchpad into a formal project with its own ClickUp list.

---

## Prerequisites

Before graduating, ensure the idea has:
- [ ] Clear scope defined
- [ ] 5+ potential subtasks identified
- [ ] Priority 1-2 assigned
- [ ] Tag: `ready-to-graduate`

---

## Workflow Steps

### 1. Capture Idea Details

```
Read the idea task from Idea Scratchpad:
- Task ID
- Task name
- Description (contains analysis if processed)
- Any subtasks already created
```

### 2. Create Project Directory

```bash
PROJECT_NAME="project-name-kebab-case"
mkdir -p /root/flourisha/01f_Flourisha_Projects/${PROJECT_NAME}
```

### 3. Create README

```bash
cat > /root/flourisha/01f_Flourisha_Projects/${PROJECT_NAME}/README.md << 'EOF'
# {Project Name}

{Description from idea task}

## Status

🚀 Active Development

## ClickUp

- **List:** {list_name}
- **List ID:** {list_id}

## Quick Links

- [ClickUp Board](https://app.clickup.com/8655078/v/li/{list_id})

## Overview

{Expanded description}

## Goals

- {Goal 1}
- {Goal 2}

## Architecture

{Technical approach if applicable}
EOF
```

### 4. Create ClickUp List

```bash
curl -X POST \
  -H "Authorization: pk_12782467_..." \
  -H "Content-Type: application/json" \
  "https://api.clickup.com/api/v2/folder/90117368142/list" \
  -d '{"name": "{Project Name}"}'
```

Save the returned `list_id`.

### 5. Create META Task

```bash
curl -X POST \
  -H "Authorization: pk_12782467_..." \
  -H "Content-Type: application/json" \
  "https://api.clickup.com/api/v2/list/{list_id}/task" \
  -d '{
    "name": "[META] {Project Name} Progress Tracker",
    "markdown_description": "## Project Overview\n\n{Description}\n\n## Session Tracking\n\nThis task coordinates multi-session work.\n\n## Key Milestones\n\n- [ ] Project setup complete\n- [ ] Core features implemented\n- [ ] Testing complete\n- [ ] Documentation done",
    "priority": 1,
    "assignees": [87375090]
  }'
```

### 6. Generate 50 Tasks

Break the project into comprehensive tasks:

**Infrastructure (Tasks 1-10, Priority 1)**
- Project setup, dependencies, configuration
- Database schema, API scaffolding
- CI/CD, deployment setup

**Core Features (Tasks 11-30, Priority 2)**
- Main user-facing functionality
- Critical business logic
- Primary integrations

**Secondary Features (Tasks 31-45, Priority 3)**
- Nice-to-have functionality
- Additional integrations
- Admin/settings features

**Polish (Tasks 46-50, Priority 4)**
- Edge cases, error handling
- Performance optimization
- Documentation, comments

### 7. Save Project Marker

```bash
cat > /root/flourisha/01f_Flourisha_Projects/${PROJECT_NAME}/.clickup_project.json << EOF
{
  "initialized": true,
  "created_at": "$(date -Iseconds)",
  "list_id": "{list_id}",
  "list_name": "{Project Name}",
  "meta_task_id": "{meta_task_id}",
  "graduated_from": "{original_idea_task_id}",
  "total_tasks": 50,
  "folder_id": "90117368142",
  "space_id": "14700061"
}
EOF
```

### 8. Close Original Idea

```bash
# Update original idea task
curl -X PUT \
  -H "Authorization: pk_12782467_..." \
  -H "Content-Type: application/json" \
  "https://api.clickup.com/api/v2/task/{idea_task_id}" \
  -d '{
    "status": "done"
  }'

# Add graduation comment
curl -X POST \
  -H "Authorization: pk_12782467_..." \
  -H "Content-Type: application/json" \
  "https://api.clickup.com/api/v2/task/{idea_task_id}/comment" \
  -d '{
    "comment_text": "✅ Graduated to project: {Project Name}\n\nList: https://app.clickup.com/8655078/v/li/{list_id}\nFolder: /root/flourisha/01f_Flourisha_Projects/{project-name}/"
  }'
```

### 9. Sync to Google Drive

```bash
flourisha-bisync
```

---

## Post-Graduation Checklist

- [ ] Project folder created in `01f_Flourisha_Projects/`
- [ ] ClickUp list created in Flourisha folder
- [ ] META task created with milestones
- [ ] 50 tasks generated with proper priorities
- [ ] `.clickup_project.json` saved
- [ ] Original idea marked `done` with link
- [ ] Synced to Google Drive

---

## Example

**Original Idea:**
```
Task: "Build AI-powered property management dashboard"
List: Idea Scratchpad
Tags: idea, ready-to-graduate
```

**After Graduation:**
```
Project Folder: /root/flourisha/01f_Flourisha_Projects/propportal-ai/
ClickUp List: "PropPortal AI" (ID: 901112xxxxx)
META Task: "[META] PropPortal AI Progress Tracker"
Tasks: 50 detailed implementation tasks
Original Idea: Closed with link to new project
```
