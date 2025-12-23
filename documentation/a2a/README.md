# A2A Protocol Documentation

**A2A (Agent-to-Agent) Protocol** integration for Flourisha AI Brain.

---

## Quick Start

1. **Read the Overview**: [overview.md](overview.md)
   - What is A2A and why we use it
   - Flourisha's A2A architecture
   - Benefits and capabilities

2. **Learn Agent Cards**: [agent-cards.md](agent-cards.md)
   - Detailed agent card specification
   - How to create and validate cards
   - Examples and best practices

3. **Explore Examples**:
   ```bash
   # View an agent card
   cat /root/flourisha/00_AI_Brain/agents/gemini-researcher/agent-card.json

   # View a skill card
   cat /root/flourisha/00_AI_Brain/skills/alex-hormozi-pitch/skill-card.json
   ```

---

## Available Documentation

| Document | Description |
|----------|-------------|
| [overview.md](overview.md) | A2A protocol overview and Flourisha integration |
| [agent-cards.md](agent-cards.md) | Complete agent card specification and guide |

---

## Quick Commands

### Validate Agent Cards
```bash
/root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh
```

### Sync Registries
```bash
# All registries
/root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --all

# Agents only
/root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --agents

# Skills only
/root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --skills
```

### Search Agents by Tag
```bash
jq '.agents[] | select(.tags[] | contains("research"))' \
  /root/flourisha/00_AI_Brain/a2a/registry/agents.json
```

### List All Skills
```bash
jq -r '.skills[] | "\(.id): \(.description)"' \
  /root/flourisha/00_AI_Brain/a2a/registry/skills.json
```

---

## Directory Structure

```
/root/flourisha/00_AI_Brain/
├── agents/                    # Agent implementations + cards
│   └── [agent]/
│       ├── AGENT.md
│       └── agent-card.json
│
├── skills/                    # Skill implementations + cards
│   └── [skill]/
│       ├── SKILL.md
│       └── skill-card.json
│
├── a2a/                       # A2A infrastructure
│   └── registry/
│       ├── agents.json        # Master agent registry
│       ├── skills.json        # Master skill registry
│       └── capabilities.json  # System capabilities
│
├── scripts/a2a/               # A2A tooling
│   ├── validate-cards.sh
│   └── sync-registry.sh
│
└── documentation/a2a/         # This directory
    ├── README.md              # This file
    ├── overview.md            # A2A overview
    └── agent-cards.md         # Agent card spec
```

---

## Key Concepts

### Agent Cards
JSON manifests declaring agent capabilities, skills, and interfaces.

### Skills
Specific capabilities an agent provides, with examples and I/O modes.

### Registry
Master index of all agents and skills for discovery.

### Capabilities
System-wide features like voice system, parallel orchestration, Google Drive sync.

### Transport
How agents communicate (internal file-based, JSON-RPC, gRPC, REST).

---

## Integration with PAI

A2A complements Flourisha's existing PAI architecture:

- **Skills** work as before, now with A2A cards for discovery
- **Agents** accessible via symlinks, enhanced with capability declarations
- **Multi-vendor** support built-in for Claude, Gemini, future AIs
- **Google Drive** sync maintained for Obsidian editing
- **Progressive disclosure** preserved (Tier 1/2/3 loading)

---

## External Resources

- **A2A Protocol**: https://a2a-protocol.org/latest/
- **A2A Specification**: https://a2a-protocol.org/latest/specification/
- **GitHub**: https://github.com/a2aproject/A2A

---

**Last Updated:** 2025-11-19
**Version:** 1.0.0
