# A2A Scripts

Helper scripts for managing A2A (Agent-to-Agent) protocol infrastructure in Flourisha AI Brain.

## Available Scripts

### `sync-registry.sh`
Regenerate registry files from current agents and skills.

**Usage:**
```bash
# Sync everything
./sync-registry.sh --all

# Sync only agents
./sync-registry.sh --agents

# Sync only skills
./sync-registry.sh --skills
```

### `validate-cards.sh`
Validate all agent cards for correct JSON syntax and required A2A fields.

**Usage:**
```bash
./validate-cards.sh
```

**Checks:**
- ✓ Valid JSON syntax
- ✓ Required fields present (agent.id, agent.name, agent.description)
- ⚠ Recommended fields (capabilities, skills)

## Quick Commands

```bash
# Navigate to scripts
cd /root/flourisha/00_AI_Brain/scripts/a2a

# Make scripts executable
chmod +x *.sh

# Validate all cards
./validate-cards.sh

# Sync registries
./sync-registry.sh --all
```

## Integration with Workflows

These scripts are designed to run:
- **After creating new agents** - to update registries
- **After modifying agent cards** - to validate changes
- **Before syncing to Google Drive** - to ensure consistency
- **After pulling from Google Drive** - to refresh registries

## Future Scripts (Planned)

- `generate-agent-card.sh` - Generate agent card from AGENT.md frontmatter
- `list-agents.sh` - List all agents with capabilities
- `find-agent.sh` - Search for agents by tag or capability
- `export-registry.sh` - Export registry in different formats (JSON, YAML, CSV)
