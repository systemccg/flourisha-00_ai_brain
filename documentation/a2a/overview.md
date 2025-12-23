# A2A Protocol Integration - Overview

**Version:** 1.0.0
**Created:** 2025-11-19
**Protocol Version:** 0.1.0

---

## What is A2A?

The **Agent-to-Agent (A2A) Protocol** is an open standard designed to enable seamless communication and collaboration between AI agents. Originally developed by Google and now managed by the Linux Foundation, it provides:

- **Universal agent interoperability** across different platforms (LangGraph, CrewAI, Claude, Gemini, etc.)
- **Standardized discovery** mechanisms for finding and selecting agents
- **Capability declaration** through Agent Cards
- **Message format standards** for consistent communication
- **Security and authorization** patterns

---

## Why A2A for Flourisha?

### Benefits

1. **External Agent Interoperability**
   - Flourisha agents can communicate with Google's Gemini agents
   - Integration with LangGraph, CrewAI, and other A2A-compliant systems
   - Participate in broader agent ecosystems

2. **Enhanced Discovery**
   - Programmatic agent and skill discovery via registries
   - Tag-based capability matching
   - Dynamic agent selection based on requirements

3. **Future-Proof Architecture**
   - Industry standard compliance
   - Multi-vendor support built-in
   - Scalable to external agent networks

4. **Better Documentation**
   - Agent capabilities clearly declared
   - Skills documented with examples
   - Input/output modes specified

---

## Flourisha A2A Architecture

### Directory Structure

```
/root/flourisha/00_AI_Brain/
├── agents/                          # Multi-vendor agent definitions
│   ├── gemini-researcher/
│   │   ├── AGENT.md                # Implementation
│   │   └── agent-card.json         # A2A capability declaration
│   ├── architect/
│   ├── engineer/
│   └── [other agents]/
│
├── skills/                          # Multi-vendor skills
│   ├── alex-hormozi-pitch/
│   │   ├── SKILL.md                # Skill definition
│   │   └── skill-card.json         # A2A capability declaration
│   ├── research/
│   └── [other skills]/
│
├── a2a/                             # A2A infrastructure
│   ├── registry/
│   │   ├── agents.json             # Master agent registry
│   │   ├── skills.json             # Master skill registry
│   │   └── capabilities.json       # System capabilities
│   └── schemas/                    # JSON schemas (future)
│
├── scripts/a2a/                     # A2A tooling
│   ├── sync-registry.sh            # Regenerate registries
│   ├── validate-cards.sh           # Validate agent cards
│   └── README.md
│
└── documentation/a2a/               # A2A documentation
    ├── overview.md                 # This file
    ├── agent-cards.md              # Agent card specification
    └── integration.md              # Integration guide
```

### Symlink Pattern

```bash
# Claude access (current)
/root/.claude/agents/ → /root/flourisha/00_AI_Brain/agents/
/root/.claude/skills/ → /root/flourisha/00_AI_Brain/skills/

# Gemini access (future)
/root/.gemini/agents/ → /root/flourisha/00_AI_Brain/agents/
/root/.gemini/skills/ → /root/flourisha/00_AI_Brain/skills/
```

**Benefits:**
- Single source of truth in AI Brain
- Multi-vendor support without duplication
- Edit once, all AIs see updates
- Syncs to Google Drive for Obsidian editing

---

## Agent Cards

Every agent has an **agent-card.json** file declaring:

- **Identity**: id, name, version, description
- **Capabilities**: streaming, push notifications, extensions
- **Skills**: What the agent can do (with examples, tags, I/O modes)
- **Transport**: How to communicate with the agent
- **Security**: Authorization requirements

**Example:**
```json
{
  "protocolVersion": "0.1.0",
  "agent": {
    "id": "gemini-researcher",
    "name": "Gemini Researcher",
    "description": "Multi-perspective research orchestrator"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "extensions": ["voice-system", "parallel-orchestration"]
  },
  "skills": [
    {
      "id": "multi-perspective-research",
      "description": "Break down queries into variations...",
      "tags": ["research", "parallel", "gemini"],
      "examples": ["Research best AI frameworks"],
      "inputModes": {"text/plain": true},
      "outputModes": {"text/markdown": true}
    }
  ]
}
```

---

## Discovery Registry

The **a2a/registry/** directory contains master registries:

### agents.json
- Lists all available agents
- Agent card URLs
- Tags and categories
- Quick lookup for agent selection

### skills.json
- Lists all available skills
- Skill card URLs
- Slash command mappings
- Categorized by type

### capabilities.json
- System-wide capabilities
- Voice system, Google Drive sync, etc.
- Transport protocols
- Extensions available

---

## Compliance with A2A Spec

Flourisha implements:

✅ **Agent Cards** - JSON manifests with capability declarations
✅ **Skills Declaration** - Each skill with tags, examples, I/O modes
✅ **Discovery Registry** - Centralized agent and skill discovery
✅ **Message Format** - Ready for Parts-based messages (TextPart, FilePart, DataPart)
✅ **Transport Layer** - Internal file-based, extensible to JSON-RPC
✅ **Security Schemes** - Authorization patterns for sensitive operations

---

## Quick Reference

### Validate All Agent Cards
```bash
/root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh
```

### Sync Registries
```bash
/root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --all
```

### Find Agent by Tag
```bash
# Search agents registry
jq '.agents[] | select(.tags[] | contains("research"))' \
  /root/flourisha/00_AI_Brain/a2a/registry/agents.json
```

### List All Skills
```bash
jq -r '.skills[] | "\(.id): \(.description)"' \
  /root/flourisha/00_AI_Brain/a2a/registry/skills.json
```

---

## Next Steps

1. **Read**: [agent-cards.md](agent-cards.md) - Detailed agent card specification
2. **Read**: [integration.md](integration.md) - Integration with external A2A systems
3. **Explore**: Existing agent cards in `agents/*/agent-card.json`
4. **Create**: New agents following A2A patterns

---

## Resources

- **A2A Protocol**: https://a2a-protocol.org/latest/
- **Agent Registry**: `/root/flourisha/00_AI_Brain/a2a/registry/agents.json`
- **Skill Registry**: `/root/flourisha/00_AI_Brain/a2a/registry/skills.json`
- **Scripts**: `/root/flourisha/00_AI_Brain/scripts/a2a/`

---

**Last Updated:** 2025-11-19
**Maintainer:** Flourisha AI Brain
