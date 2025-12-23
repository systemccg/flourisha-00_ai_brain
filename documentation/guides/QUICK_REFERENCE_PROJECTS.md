# Project Creation Quick Reference

## Create New Project

```bash
# Interactive mode (recommended for first-time)
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh

# Quick mode with parameters
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  -t [template] \
  -n "Project Name" \
  -q
```

## Templates Available

| Template | Use For | Command Shortcut |
|----------|---------|-----------------|
| `client` | Client work, consulting | `-t client` |
| `research` | Research, analysis | `-t research` |
| `development` | Software projects | `-t development` |
| `general` | Miscellaneous | `-t general` |

## Examples

```bash
# Client project
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh -t client -n "Acme Corp" -q

# Research project
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh -t research -n "Market Analysis" -q

# Development project
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh -t development -n "API Redesign" -q
```

## After Creation

```bash
# Navigate to project
cd /root/flourisha/01f_Flourisha_Projects/[project-name]

# Sync to Google Drive
flourisha-bisync

# Or edit in Obsidian (auto-syncs)
```

## Full Documentation

See: `/root/flourisha/00_AI_Brain/documentation/projects/PROJECT_CREATION_GUIDE.md`
